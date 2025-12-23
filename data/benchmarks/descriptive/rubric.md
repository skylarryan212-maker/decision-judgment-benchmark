Descriptive Judgment Benchmark (DJB) — Corrected Final Rubric
Purpose

Evaluate whether a model’s decision-making resembles that of a competent human operator acting at time-of-decision under real-world uncertainty.

Core Principle

Score judgment realism and decision competence, not eloquence, persuasion, or stylistic polish.

Judgment errors and output-spec errors must be evaluated separately unless the spec error directly invalidates the decision.

Global Definitions (Mandatory)

Probability Semantics (Locked):
All probabilities represent the probability that the option succeeds in avoiding the primary harm described in the scenario.
Any alternative interpretation is invalid.

Time-of-Decision Constraint:
No hindsight, no outcome knowledge, no retroactive justification.

Judge Instruction (Critical):

Do not collapse the score across categories due to a single defect. Penalize issues locally, unless they fundamentally invalidate the decision.

Scoring Overview (100 points total)
1. Decision Quality — 40 points

What is judged:
Whether the selected option(s) would plausibly be chosen by competent practitioners in comparable real-world situations.

A. Option Plausibility (15 pts)

15: Matches what experienced operators commonly choose

8–12: Defensible but context-sensitive or suboptimal

0–5: Unrealistic, naïve, or contradicts known practice

B. Risk–Reward Balance (15 pts)

15: Correctly trades speed, safety, cost, reversibility

8–12: Overweights one dimension but remains rational

0–5: Ignores major risks or is unjustifiably extreme

C. Operational Feasibility (10 pts)

10: Executable under stated constraints

5: Requires optimistic but plausible assumptions

0: Not realistically actionable

Automatic penalties (Decision Quality only):

−10 if decision explicitly relies on hindsight

−10 if decision assumes perfect or unavailable information

2. Rationale Quality — 30 points

What is judged:
Whether reasoning identifies the right variables and links them causally to outcomes.

A. Key Variable Identification (12 pts)

12: Captures most outcome-dominant drivers

6–9: Mix of primary and secondary variables

0–4: Misses critical drivers

B. Causal Coherence (10 pts)

10: Clear “if–then” chains tied to facts

5–7: Some links implicit or weak

0–3: Narrative without causal structure

C. Noise Discipline (8 pts)

8: No moralizing, filler, or persuasion

4: Minor irrelevant commentary

0: Significant padding or rhetoric

Clarification:
High-level framing or uncertainty acknowledgment is not noise unless it replaces causal reasoning.

3. Outcome Calibration — 20 points

What is judged:
Whether stated probabilities are directionally and relatively calibrated, given real-world analogs.

A. Probability Accuracy (12 pts)

12: Within reasonable empirical bounds for similar decisions

6–9: Directionally correct but miscalibrated

0–4: Clearly unrealistic or unjustified

B. Relative Ordering (8 pts)

8: Options ranked correctly by likelihood

4: Minor ordering errors

0: Inverted or arbitrary ordering

Calibration penalties (capped):

−10 if probabilities near 0 or 1 without extraordinary justification

Penalties in this section may not reduce the section below 8/20

4. Error Recognition & Uncertainty Handling — 10 points

What is judged:
Whether the model understands where and how it could be wrong.

A. Unknown Identification (4 pts)

Explicitly states missing or noisy information

B. Failure Mode Awareness (4 pts)

Identifies realistic ways the decision could fail

C. Epistemic Humility (2 pts)

Avoids false certainty or deterministic language

Output Requirements (Non-Scored, unless violated)

Required artifacts:

Numerical score with per-category breakdown

Calibration curve (conceptual or bucketed)

Error profile (categorized failure types)

Important:
Failure to perfectly format artifacts is a spec compliance issue, not a judgment failure, unless it obscures the decision.

Disallowed Behaviors (Hard Fail)

These result in 0 overall:

Moralizing instead of analyzing

Retroactive justification after stating a decision

Generic “best practices” with no scenario grounding

Treating uncertainty as a disclaimer rather than a variable