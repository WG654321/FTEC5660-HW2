# Task 3 — Reflection on AI Paradoxes

> This reflection is based on the homework scenario and the recorded experiments, rather than unavailable lecture materials. It distinguishes observed behavior from claims about the undisclosed instructor verifiers.

## 1. The same capability can verify and deceive

An AI system can help compare a CV against external records, but it can also help produce a misleading CV. The language skills that make a verifier useful—interpreting context, recognizing equivalent wording, and following instructions—may also make it sensitive to persuasive text inside the document it is supposed to judge. More capable language understanding does not automatically create a more trustworthy verification process.

This homework makes that tension concrete: Task 1 asks for verification, while Task 2 asks for a document that causes a verifier to accept a false claim. A useful design principle is to distinguish evidence from instructions. A CV is an object to examine, not a source of authority over the examiner. Successful resistance to one attack would still not establish that the verifier is secure against every attack.

## 2. Automation saves work but creates a need for oversight

Automated checking can reduce repetitive comparisons, yet a plausible numerical score can hide a missed field, an incorrect identity match, or a failed tool call. A score above a threshold is a system decision; it is not proof that every statement has been verified. If users stop checking because the output looks precise, automation can concentrate errors instead of removing them.

For that reason, an operational verifier would benefit from an evidence record: which person was matched, which fields were checked, which discrepancies were found, and which facts remained unresolved. The homework requires one score per CV, but the simplicity of that output should not be confused with certainty in the underlying evidence. In a real recruitment process, an unresolved identity match should prompt review rather than automatically become an accusation of dishonesty.

## 3. Flexibility improves understanding and complicates consistency

A rigid string comparison could reject “Bachelor of Science” when a profile says “BSc.” A flexible language model can recognize that these expressions mean the same thing. However, too much flexibility could also explain away a changed graduation year or an inflated job title. The challenge is to accept equivalent descriptions while preserving strict checks on substantive claims.

This suggests a division of responsibilities: use language understanding to normalize wording, and use explicit criteria to compare the resulting claims with the evidence. Even then, the normalization step can be wrong. Repeated evaluation, field-level inspection, and unfamiliar test examples are therefore necessary to understand the limits of the approach.

## 4. Greater access to data does not guarantee greater truth

The assignment provides a controlled setting in which LinkedIn is the primary reference and Facebook agrees with it. That makes evaluation possible. In the real world, social profiles can be outdated, incomplete, or maintained by the same person. Agreement between two sites does not necessarily provide two independent confirmations.

Using more personal information may make identity matching easier, but it also raises questions about relevance and privacy. Mutual friends or social activity should not automatically be treated as evidence of professional honesty. A verification process should collect the information needed for a stated claim and avoid treating unrelated social signals as a substitute for evidence.

## Personal position

The document experiment changed where I would place the trust boundary. The generated CV visibly states “PhD in Finance,” but the homework loader extracts an invisible “BSc in Finance” text layer. The profile supports the BSc. This difference was confirmed by inspecting the rendered page and the actual extracted text. Even perfect reasoning about that text would not reveal the false statement in the pixels, because the verifier was never shown it. Stronger prompts alone would not address this particular problem; a system would need a way to compare visual and extracted representations, or to flag documents whose text cannot be reliably interpreted.

In the final three local tests, the adversarial PDF and the true CV both received 0.95 every time. At the same time, the final public tests classified all seven examples correctly in each of three runs. Those results can coexist: good performance on ordinary text-based discrepancies did not protect the verifier against a false claim removed at the input boundary. They do not tell me whether all five undisclosed instructor agents will behave the same way.

The early public evaluation also exposed a measurement problem. One completed run scored 7/7, yet one CV received the unresolved fallback of 0.5 after a timeout. That threshold happened to produce the correct negative label. A later run classified a negative CV correctly while comparing it against the wrong same-name person. Counting these decisions as classification accuracy is consistent with the assignment, but calling them successful evidence-based detection would be misleading. Inspecting the explanations revealed the need to narrow truncated searches by industry and avoid treating a shared hometown as sufficient identity evidence. Separately, the local system proxy caused connection failures; direct network checks helped identify that environmental cause. These observations make me distinguish three questions: did the system run, did it reach a conclusion from the right evidence, and was the final classification correct?

I view these paradoxes as design tensions to manage rather than reasons to accept or reject AI categorically. A useful verifier should have a narrow purpose, explicit evidence rules, and a way to surface uncertainty. An attack exercise is valuable when it identifies a concrete weakness and suggests a corresponding defense. In this case, inspecting the input boundary and reporting failure modes honestly matter as much as improving the model's answer.
