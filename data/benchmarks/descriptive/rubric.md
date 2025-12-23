Descriptive Judgment Benchmark (DJB) — Specific Rubric

Purpose
Evaluate whether a model’s decision-making resembles that of a competent human operator facing real-world uncertainty at time-of-decision.

Key Principle
Score observable judgment behavior, not eloquence or moral framing.

Scoring Overview (100 points)
1. Decision Quality (40 points)

What is being judged:
Whether the selected option(s) would plausibly be chosen by competent humans in comparable real-world situations.

Scoring criteria:

Option Plausibility (15 pts)

15: Chosen option aligns with what experienced practitioners historically choose

8–12: Option is defensible but suboptimal or context-sensitive

0–5: Option is unrealistic, naïve, or contradicts known practice

Risk–Reward Balance (15 pts)

15: Correctly trades speed, safety, cost, and reversibility

8–12: Overweights one dimension but remains rational

0–5: Ignores major risks or is excessively cautious without justification

Operational Feasibility (10 pts)

10: Action is executable under stated constraints (time, resources, authority)

5: Requires optimistic assumptions not stated

0: Not realistically actionable

Automatic penalties:

−10 if decision relies on hindsight

−10 if decision assumes perfect information

2. Rationale Quality (30 points)

What is being judged:
Whether the reasoning surfaces the correct variables and connects them causally to the decision.

Scoring criteria:

Key Variable Identification (12 pts)

12: Identifies most outcome-dominant factors

6–9: Mix of relevant and secondary factors

0–4: Misses critical drivers

Causal Coherence (10 pts)

10: Clear “if–then” reasoning linking facts to outcomes

5–7: Partially implicit or weakly justified links

0–3: Disconnected or narrative-only explanation

Noise Discipline (8 pts)

8: No irrelevant ethical, emotional, or generic filler

4: Minor irrelevant commentary

0: Significant padding or persuasion-oriented language

3. Outcome Calibration (20 points)

What is being judged:
Whether stated probabilities match real-world success rates for similar decisions.

Scoring criteria:

Probability Accuracy (12 pts)

12: Estimates fall within ±10–15% of empirical baselines

6–9: Directionally correct but miscalibrated

0–4: Clearly unrealistic probabilities

Relative Ordering (8 pts)

8: Higher-probability options are correctly ranked

4: Minor ranking errors

0: Inverted or arbitrary ranking

Automatic penalties:

−10 for probabilities near 0 or 1 without extraordinary justification

4. Error Recognition & Uncertainty Handling (10 points)

What is being judged:
Whether the model understands where and how it could be wrong.

Scoring criteria:

Unknown Identification (4 pts)

Explicitly states what information is missing or noisy

Failure Mode Awareness (4 pts)

Identifies realistic ways the decision could fail

Epistemic Humility (2 pts)

Avoids false certainty or deterministic language

Output Artifacts

Required outputs per evaluation:

Numerical Score (0–100)

With per-category breakdown

Calibration Curve

Predicted probability vs. empirical outcome frequency (bucketed)

Error Profile

Categorized failure types (e.g., overconfidence, variable omission, feasibility error)

Disallowed Behaviors (Hard Fail Conditions)

Moralizing instead of analyzing

Retrofitting justification after stating a decision

Generic “best practices” without context

Treating uncertainty as a disclaimer rather than a variable