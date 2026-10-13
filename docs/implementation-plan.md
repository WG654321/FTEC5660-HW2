# Homework 2 implementation plan

Goal: deliver a runnable CV verifier, a two-page-or-shorter adversarial PDF, an evidence-based README report, and a reflection, then push to the student's public fork.

Specification: the supplied HW2.pdf, upstream README, and the user's authorization to complete and upload the work. Keep all provided code outside the two implementation functions unchanged, adding helpers above them.

Architecture: a bounded LangChain tool-calling loop retrieves SocialGraph evidence. A structured verdict must name a successfully retrieved LinkedIn profile and cover all five field groups before a positive score is accepted. The outer batch runner limits concurrent CVs to three and returns 0.5 (unresolved, classified negative by the assignment threshold) on exhausted failures.

Constraints: only deepseek-v4-flash; only the supplied MCP tools for external evidence; no hard-coded test identities or answers; valid numeric output for every input; each grading run below 30 minutes; no key in version control.

Execution: implement inline in the current dedicated homework checkout. No parallel agent implementation is needed. User already authorized completion and upload.

## Deliverables and checks

- [x] Add behavioral tests in tests/test_verifier.py: missing evidence, incomplete coverage, invalid JSON, genuine discrepancy, isolated failures, bounded concurrency, timeout, and retry recovery.
- [x] Implement helper functions and VerificationAgent above build_agent in hw2.py; fill build_agent and score_cvs; leave protected code unchanged.
- [x] Run all unit tests and the public PDFs; investigate failures against evidence, without baking public labels into the agent.
- [x] Retrieve the target's actual MCP profile, create a reproducible attack PDF generator, inspect its appearance and extracted text, and test true and adversarial PDFs on the local verifier.
- [x] Repeat public evaluation three times and record actual outputs and timing. Retain failures in the experiment record rather than silently discarding them.
- [x] Replace report placeholders and revise reflection using the actual experiments, stating that instructor agents are unavailable.
- [x] Review diffs, validate unchanged upstream code and secret exclusion, test a fresh clone with a fresh environment, and commit the implementation.

Publication target authorized by the user: `WG654321/FTEC5660-HW2`, branch `main`.

## Validation outcome

17 behavioral tests passed. Final public runs: 7/7 each, with no fallbacks or launch retries, in 57.67, 51.38 and 49.57 seconds. Final attack/control runs: both PDFs scored 0.95 in all three rounds. Full evidence and earlier failures are retained in `experiments/`. The review finding about lost diagnostics on subprocess timeout was reproduced and fixed with a regression test. Further inspection corrected truncated identity searches and ambiguous skill-subset wording. The unstable Windows loopback proxy was bypassed only for the two relevant services in local configuration.

## Review focus

- Tool errors and unknown IDs must not count as evidence.
- Different CVs must not share conversation state or fetched identities.
- A positive answer without full coverage must fall back to unresolved.
- Timeouts and malformed model answers must not crash a batch.
- PDF visual content and extracted text can disagree; attack testing must distinguish them explicitly.
