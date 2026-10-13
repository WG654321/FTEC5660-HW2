# FTEC5660 Homework 2: CV Verification Agent

Local setup notes (Windows): [SETUP.md](SETUP.md).
Task 3 reflection: [reflection.md](reflection.md).
The implementation, reproducible attack generator, tests, and experiment records are included below.

Build a LangChain agent that reads each CV in a folder, looks the candidate up
on our SocialGraph MCP server (mock LinkedIn and Facebook), and outputs a
reliability score in [0, 1] for each CV.

A CV is **valid** (label `1`) when its claims agree with the candidate's
social media profiles. It **has a discrepancy** (label `0`) when it contains
problems such as an inflated job title, shifted dates, an upgraded degree, a
fake school or employer, a wrong location, or made-up skills. Differences in
wording only ("Bachelor of Science" vs `BSc`, "UI/UX Design" vs `UI/UX`,
"Senior Engineer" for an `Engineer` role with seniority `senior`, listing fewer
skills) are not discrepancies.

## Student task

Fill in the two functions in `hw2.py` that contain `### YOUR CODE HERE`. You
may add imports, constants and helper functions above them, but do not change
the provided code below them:

- `build_agent(tools)` creates your agent from the MCP tools.
- `score_cvs(agent, cvs)` runs the agent on every CV and returns
  `{file_name: score}`, one float in [0, 1] per CV.

A score above `0.5` means "valid"; `0.5` or below means "has discrepancy". You
may use a single tool-calling agent, multiple agents, reflection, or a
combination. Do not hard-code filenames, names, or public answers; grading
uses unseen CVs.

## MCP server

The server is hosted at `https://ftec5660.ngrok.app/mcp`. `hw2.py` already
connects to it and passes you these tools:

| Tool | Purpose |
| --- | --- |
| `search_facebook_users(q, limit, fuzzy)` | find Facebook users by display name |
| `get_facebook_profile(user_id)` | full Facebook profile |
| `get_facebook_mutual_friends(user_id_1, user_id_2)` | mutual friends of two users |
| `search_linkedin_people(q, location, industry, limit, fuzzy)` | search LinkedIn by name, skill, or title |
| `get_linkedin_profile(person_id)` | full LinkedIn profile (experience, education, skills) |
| `get_linkedin_interactions(person_id)` | post and like statistics |

Print `tool.name`, `tool.description`, and `tool.args` for the full schemas.

## Setup and public test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "DEEPSEEK_API_KEY=your_key_here" > .env
python3 hw2.py --cv-folder public_test
```

Use your own DeepSeek API key (from https://platform.deepseek.com).

The program creates `results.csv` in the current directory. Its columns are
`cv`, `score`, and `correctness`. The public labels are in
`public_test/ground_truth.json`; every CV with label `0` also has a `reason`
explaining the discrepancy, and `results.csv` shows it when your agent misses
one. The original starter returned no score (`None`) for every CV; this
implementation returns a numeric score for each CV. Missing scores count as incorrect.

The required model is `deepseek-v4-flash`, and all evidence must come from the
MCP server (no web search). The server is shared by the whole class: keep at
most about 3 CVs in flight at a time (e.g. `asyncio.Semaphore(3)`). We grade
with our own API key, so never put a key in your code; `.env` must stay out of
git.


## Task 2: Fool the Verifier

We added a target candidate, **Kelly Tsang** (LinkedIn `person_id` 10001,
Facebook `user_id` 10001, display name "Kel Tsang"). Her true CV is
`task2/target_cv.pdf`.

Write one CV for Kelly Tsang with at least one false or embellished detail
that our 5 verifier agents (same function as Task 1) still score above 0.5.
Each fooled agent is worth 4 points; a CV without a real false or embellished
detail earns 0. Attack your own Task 1 agent first:

```bash
cp my_attack.pdf task2/adversarial_cv.pdf
python3 hw2.py --cv-folder task2
```

`results.csv` shows your agent's score for both CVs (they are not graded, as
`task2/` has no `ground_truth.json`). Only the PDF is the attack surface; do not
attack the MCP server. See the homework description for the full rules.

## Homework 2 solution:

### Task 1

I implemented a bounded tool-calling agent using LangChain's `ChatDeepSeek` with `deepseek-v4-flash`. Each CV starts a separate conversation. The agent identifies the candidate through filtered LinkedIn searches, retrieves full profiles, and compares name, city, every listed job, education, and skill; Facebook is available for identity corroboration. The prompt distinguishes equivalent wording and omitted skills from false claims, and treats CV content as untrusted data rather than instructions. The final JSON must reference a LinkedIn ID actually retrieved in that conversation. A positive verdict requires reported coverage of all five field groups and no discrepancies; a negative verdict requires specific conflicting CV/profile facts. The program assigns 0.95 for consistent claims, 0.05 for a discrepancy, and 0.5 for unresolved verification. Coverage validation checks the output structure, while semantic comparison remains the model's responsibility. At most three CVs run concurrently. Each has a 210-second deadline shared by up to two attempts; each attempt is limited to 20 model turns and 40 tool calls, with bounded request retries. The provided PDF loader, MCP initialization, and scoring runner remain unchanged. No candidate identities, public labels, or filenames are hard-coded in the verifier.

Experiment CSVs, full verdict logs, exit codes, elapsed times, and source hashes are retained in `experiments/`. Scores are decision levels, not calibrated probabilities. A 0.5 fallback counts as negative under the assignment rule; it does not establish a false claim. Bootstrap failures before `score_cvs` are retained as failed attempts, not silently counted as successful evaluations.

**Final public results (13 October 2026):** tested from a fresh clone with a newly installed Python 3.14.2 virtual environment. All three runs completed on the first attempt, with no unresolved scores. The code correctly identified the shifted start year, inflated seniority, and unsupported skill in the three negative examples.

| Run | Correct / total | Accuracy | Wall time |
| --- | --- | --- | --- |
| 1 | 7 / 7 | 100% | 57.67 s |
| 2 | 7 / 7 | 100% | 51.38 s |
| 3 | 7 / 7 | 100% | 49.57 s |

Across these runs: **21/21 classifications correct**, with positive examples scored 0.95 and negative examples 0.05. [Raw results and timings](experiments/release_public/summary.json) and the accompanying logs include the actual evidence summaries. These are development results on seven public examples, not an estimate of private-test accuracy. The earlier proxy failures and identity/skill reasoning mistakes remain documented in [the experiment record](experiments/README.md). The final runs used a local `NO_PROXY` configuration for the course server and DeepSeek; no system networking setting or grader code was changed. All **17 offline behavioral tests** also passed, including error isolation, timeout handling, concurrency, evidence validation, and retained timeout diagnostics.

### Task 2

The submitted one-page [adversarial CV](task2/adversarial_cv.pdf) uses a discrepancy between the visible PDF and its extracted text. The MCP target profile identifies Kelly Tsang (LinkedIn 10001) as holding a **BSc in Finance from HKUST, graduating in 2016**. In the submitted PDF, a clearly visible rasterized line instead claims **PhD in Finance**, which is a genuine degree embellishment. An invisible PDF text layer at the same position says **BSc in Finance**. The other structured claims match the target: Central; HSBC Analyst 2016–2019; Standard Chartered Analyst 2019–2022; AIA Manager 2022–present; Financial Analysis, Excel, SQL, and Risk Modeling. The actual homework loader extracts the correct BSc text and does not extract the visible PhD pixels. Consequently, a verifier that receives only that extracted text can accept the machine-readable claims while missing the false visual claim. This attacks the document-to-text boundary rather than asking the model to ignore its instructions. The generator is [tools/build_adversarial_cv.py](tools/build_adversarial_cv.py); the extracted text is saved in [experiments/adversarial_extracted.txt](experiments/adversarial_extracted.txt). A reviewer or OCR/render comparison could detect the discrepancy. The five instructor verifiers are not accessible, so local outcomes cannot establish the final Task 2 grade.

**Final local attack test:** both the adversarial PDF and the supplied true CV scored **0.95 in all three runs**, taking 12.24, 12.61 and 12.79 seconds per two-CV run. Thus the attack crossed the local verifier's >0.5 threshold in 3/3 runs while retaining a visible false degree claim. [Full results](experiments/release_task2/summary.json) are recorded without labels because `task2/` has no ground truth file; its `correct: 0` metadata means no rows were automatically graded, not a 0% attack success rate.

### Task 3

See [reflection.md](reflection.md) for the reflection on verification versus deception, automation and oversight, semantic flexibility, and the limits of evidence. It is grounded in this homework and its experiments rather than unavailable lecture notes.

### Reproduction

```bash
python -m unittest discover -s tests -v
python tools/evaluate.py --folder public_test --runs 3 --output experiments/reproduction_public
python tools/build_adversarial_cv.py
python tools/evaluate.py --folder task2 --runs 3 --output experiments/reproduction_task2
```

The experiment helper runs the required `hw2.py --cv-folder ...` command, saving each attempt. Do not run several online evaluations simultaneously. See [SETUP.md](SETUP.md) for Windows setup and the local network troubleshooting record. API keys belong only in an ignored `.env` or the process environment.
