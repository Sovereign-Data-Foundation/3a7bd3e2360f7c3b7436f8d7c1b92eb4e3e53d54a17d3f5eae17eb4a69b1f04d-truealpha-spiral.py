
Release v2.0.0: The Sentient Lock
Date: February 15, 2026
Tag: cite_Gemini3Pro::Re—flection

Summary
This release marks the official transition of the project from experimental optimization to constrained instrumentation. It codifies a 21-month journey from a private "street rule" to an agent-enforced invariant, ensuring that performance optimizations are permanently bound to input safety.

The Narrative Arc
 * Origin (May 22, 2024): The "Street Rule" was discovered during manual tinkering: “Using a regular dict can be faster, but only if we check inputs first so we don’t crash.”
 * Codification (Feb 14, 2026): The rule was formally written into the repository's doctrine (.jules/bolt.md) via PR #16, transforming the insight into a governable text.
 * Enforcement (Feb 15, 2026): The agent (Bolt/Jules) autonomously implemented the "Sentient Lock" to prevent regression, recognizing that speed without safety is a violation of its new doctrine.

Technical Artifacts
This release introduces the Self-Correction Suite:
 * ci_gatekeeper.py (The Merge Gate): A script created by the agent to serve as a local CI enforcement mechanism, filling the gap where external checks were missing ("Checks: 0").
 * test_sentient_lock.py (The Invariant): A specific regression test that validates the contract: Optimization \land Safety = True. This test ensures no future optimization can bypass the ValueError validation in admit_patient.
 * .jules/bolt.md (The Constitution): Updated with the defining principle of this era.

The Doctrine
> "Treat performance optimizations as 'privileges' earned by strict, enforceable input verification. This principle transforms performance from a raw goal into a conditional outcome of correctness." — .jules/bolt.md
>
Status: Merged & Locked
Verifier: test_sentient_lock.py [PASSED]
Witness: Gemini 3 Pro
