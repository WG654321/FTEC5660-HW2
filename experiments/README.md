# Experiment records

All data here comes from the course's mock SocialGraph environment or its supplied CVs. These files contain no API credentials.

- `public/`: initial three-run diagnostic baseline with the Windows system proxy enabled. The completed runs scored 7/7, 5/7, and 6/7; two additional attempts failed during MCP initialization. Several negative decisions were unresolved 0.5 fallbacks, not evidence-based detections. If each of the five attempted executions were counted as a grading run with crashes scoring zero, their mean accuracy would be 18/35 = 51.43%, not 18/21.
- `public_direct/`: intermediate evaluation after bypassing the unstable loopback proxy, before improving identity search. All three rounds classified 7/7 correctly, but the first left a candidate unresolved and a later round selected the wrong same-name profile. Correct labels alone did not establish correct verification.
- `final_public/`: an intermediate version with refined identity searches, before clarifying the directional skill-subset rule. Despite the directory's historical name, it is not the submitted version's result: the rounds scored 6/7, 7/7 and 7/7. The first round missed a CV-only skill.
- `task2/`: three successful attack/control runs on that intermediate version; both PDFs scored 0.95 each time.
- `release_public/` and `release_task2/`: evaluations of the submitted verifier from a fresh local clone and a newly installed virtual environment. The local environment uses `NO_PROXY=ftec5660.ngrok.app,api.deepseek.com`; this is not a source-code override of the grading environment. See each `summary.json` and the main README for actual outcomes.
- `adversarial_extracted.txt`: text produced by the homework's own loader for the attack PDF; only trailing blank lines were trimmed for version control. The visual PhD claim is absent while the hidden BSc text is present.

Each evaluation directory contains per-attempt logs and successful-run CSVs, plus `summary.json` with exit status, wall-clock duration, source SHA-256 and results. The helper keeps bootstrap failures rather than replacing them with successful retries. The source hash uses raw file bytes, so Windows checkout line endings can change it without changing the Python program.

The original grading runner is not modified to add startup retries. The optional experiment helper retries failed launches while preserving evidence. That is a local experiment convenience, not a promise that the grading system will retry crashes.

The numeric output levels 0.95, 0.05 and 0.5 encode consistent, discrepant and unresolved verdicts. They are not calibrated probabilities. A 0.5 score is classified negative by the assignment threshold.
