import asyncio
import json
import unittest
from unittest.mock import patch

import hw2


class VerdictTests(unittest.TestCase):
    def verdict(self, **changes):
        result = {
            "status": "valid", "profile_id": 42,
            "checked_fields": ["name", "city", "jobs", "education", "skills"],
            "discrepancies": [], "summary": "All claims agree with the retrieved profile.",
        }
        result.update(changes)
        return json.dumps(result)

    def test_valid_requires_retrieved_evidence(self):
        with self.assertRaises(ValueError):
            hw2.validate_verdict(self.verdict(), set())

    def test_full_verified_verdict_gets_positive_score(self):
        self.assertEqual(hw2.validate_verdict(self.verdict(), {42})["score"], 0.95)

    def test_missing_coverage_cannot_get_positive_score(self):
        with self.assertRaises(ValueError):
            hw2.validate_verdict(self.verdict(checked_fields=["name"]), {42})

    def test_discrepancy_requires_specific_evidence(self):
        with self.assertRaises(ValueError):
            hw2.validate_verdict(self.verdict(status="discrepancy"), {42})
        claim = {"field": "jobs", "cv": "2021", "evidence": "2020"}
        result = hw2.validate_verdict(self.verdict(status="discrepancy", discrepancies=[claim]), {42})
        self.assertEqual(result["score"], 0.05)

    def test_valid_cannot_hide_discrepancies(self):
        with self.assertRaises(ValueError):
            hw2.validate_verdict(self.verdict(discrepancies=[{"field": "skills"}]), {42})

    def test_malformed_outputs_rejected(self):
        for text in ["0.95", "[]", "NaN", "looks fine", "{}"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                hw2.validate_verdict(text, {42})

    def test_uncertain_is_not_accused_of_specific_discrepancy(self):
        text = self.verdict(status="uncertain", profile_id=None, checked_fields=[])
        self.assertEqual(hw2.validate_verdict(text, set())["score"], 0.5)


class BatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_one_failure_does_not_destroy_other_scores(self):
        class Agent:
            async def ainvoke(self, payload):
                if payload["cv"] == "broken":
                    raise RuntimeError("simulated failure")
                return {"score": 0.95, "summary": "verified"}
        scores = await hw2.score_cvs(Agent(), {"a.pdf": "good", "b.pdf": "broken"})
        self.assertEqual(scores, {"a.pdf": 0.95, "b.pdf": 0.5})

    async def test_transient_failure_recovers(self):
        class Agent:
            calls = 0
            async def ainvoke(self, payload):
                self.calls += 1
                if self.calls == 1:
                    raise RuntimeError("transient")
                return {"score": 0.05, "summary": "mismatch"}
        self.assertEqual(await hw2.score_cvs(Agent(), {"a": "text"}), {"a": 0.05})

    async def test_concurrency_never_exceeds_three(self):
        class Agent:
            active = 0
            peak = 0
            async def ainvoke(self, payload):
                self.active += 1
                self.peak = max(self.peak, self.active)
                await asyncio.sleep(0.01)
                self.active -= 1
                return {"score": 0.95, "summary": "verified"}
        agent = Agent()
        scores = await hw2.score_cvs(agent, {str(i): "text" for i in range(8)})
        self.assertEqual(len(scores), 8)
        self.assertEqual(agent.peak, 3)
        self.assertTrue(all(score == 0.95 for score in scores.values()))

    async def test_timeout_produces_score(self):
        class Agent:
            async def ainvoke(self, payload):
                await asyncio.sleep(5)
        with patch.object(hw2, "CV_TIMEOUT", 0.02):
            self.assertEqual(await hw2.score_cvs(Agent(), {"slow": "text"}), {"slow": 0.5})

    async def test_invalid_scores_are_not_forwarded(self):
        class Agent:
            async def ainvoke(self, payload):
                return {"score": float("nan"), "summary": "invalid"}
        self.assertEqual(await hw2.score_cvs(Agent(), {"bad": "text"}), {"bad": 0.5})


class AgentLoopTests(unittest.IsolatedAsyncioTestCase):
    def fixture(self, profile_result, final_status="valid"):
        from langchain_core.messages import AIMessage
        verdict = {"status": final_status, "profile_id": 42,
                   "checked_fields": ["name", "city", "jobs", "education", "skills"],
                   "discrepancies": [], "summary": "Compared all listed facts."}

        class Model:
            def bind_tools(self, tools):
                return self
            async def ainvoke(self, messages):
                if len(messages) == 2:
                    return AIMessage(content="", tool_calls=[
                        {"name": "get_linkedin_profile", "args": {"person_id": 42},
                         "id": "profile-call", "type": "tool_call"}])
                if messages[-1].type == "human":
                    return AIMessage(content=json.dumps({**verdict, "status": "uncertain"}))
                return AIMessage(content=json.dumps(verdict))

        class Tool:
            name = "get_linkedin_profile"
            async def ainvoke(self, args):
                return [{"type": "text", "text": json.dumps(profile_result)}]

        return hw2.VerificationAgent(Model(), [Tool()])

    async def test_successful_mcp_profile_allows_verdict(self):
        agent = self.fixture({"id": 42, "name": "Test Person", "experience": [],
                              "education": [], "skills": []})
        result = await agent.ainvoke({"cv": "Test Person"})
        self.assertEqual(result["score"], 0.95)

    async def test_unknown_profile_error_cannot_support_valid_verdict(self):
        agent = self.fixture({"error": "Unknown id"})
        result = await agent.ainvoke({"cv": "Test Person"})
        self.assertEqual(result["score"], 0.5)

    async def test_wrong_id_response_cannot_support_valid_verdict(self):
        agent = self.fixture({"id": 99, "name": "Other Person", "experience": [],
                              "education": [], "skills": []})
        result = await agent.ainvoke({"cv": "Test Person"})
        self.assertEqual(result["score"], 0.5)

    async def test_per_cv_state_is_independent(self):
        from langchain_core.messages import AIMessage

        class Model:
            def bind_tools(self, tools):
                return self
            async def ainvoke(self, messages):
                cv = json.loads(messages[1].content.split("\n", 1)[1])["cv_text"]
                if cv == "with evidence" and len(messages) == 2:
                    return AIMessage(content="", tool_calls=[
                        {"name": "get_linkedin_profile", "args": {"person_id": 42},
                         "id": "call", "type": "tool_call"}])
                repaired = messages[-1].type == "human" and len(messages) > 2
                return AIMessage(content=json.dumps({
                    "status": "uncertain" if repaired else "valid", "profile_id": 42,
                    "checked_fields": list(hw2.FIELD_GROUPS), "discrepancies": [],
                    "summary": "Candidate comparison."}))

        class Tool:
            name = "get_linkedin_profile"
            async def ainvoke(self, args):
                return {"id": 42, "name": "Test", "experience": [], "education": [], "skills": []}

        agent = hw2.VerificationAgent(Model(), [Tool()])
        first = await agent.ainvoke({"cv": "with evidence"})
        second = await agent.ainvoke({"cv": "without evidence"})
        self.assertEqual(first["score"], 0.95)
        self.assertEqual(second["score"], 0.5)


if __name__ == "__main__":
    unittest.main()
