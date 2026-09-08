# Nonlinear budgets and actual household outcomes

## Explicit nonlinear schedules

A local MTR cannot describe a worker's alternatives across a bracket boundary or a benefit cliff. The nonlinear implementation therefore accepts a net-income function $b(y)$ over an explicit earnings domain. The worker maximizes $b(y)-\psi(y/w)^{1+1/\varepsilon}/(1+1/\varepsilon)$. On a known affine segment, utility is strictly concave, so candidate maxima are its stationary point and feasible endpoints. Evaluating candidates across every segment finds the global maximum when it exists.

The schedule explicitly assigns each discontinuity's threshold to one side. If a benefit disappears at a threshold and utility approaches a superior value from below without attaining it, the continuous choice problem can have a supremum but no maximizer. The solver reports this case. It does not move the threshold or substitute an arbitrary epsilon. A finite earnings grid is an alternative economic choice set with an attained optimum.

Earnings subsidies, negative net-income slopes, and discontinuous transfers are permitted. None are transformed into a tax rate capped at 99%. The exact nonlinear accounting compares an informed choice with the choice under a separate perceived budget, then evaluates both on the true budget. Private regret is nonnegative on the common feasible choice set. The change in $y-b(y)$ supplies the net-revenue term only to the extent that the budget measures all relevant taxes and transfers. The government's complete fiscal cost can differ when the budget omits benefits, externalities, or costs whose valuation differs from consumption.

The numerical examples use a progressive schedule with net-income slopes 0.9 below $30,000 and 0.65 above, a subsidy schedule with slopes 1.2 below $15,000 and 0.7 above, and an $8,000 benefit paid through $45,000 earnings that disappears above that point. The progressive and subsidy budgets are continuous; the cliff assigns the threshold to the benefit-receiving segment. Perceived net-income slopes are constant at 0.75, 0.8, and 0.7 respectively. Each example uses the illustrative worker's preferences and a common feasible earnings range from zero to $100,000. All amounts are assumed.

{{< include generated/nonlinear.md >}}

## PolicyEngine household grid

A separate adapter executes the pinned PolicyEngine household model [@policyengine2026] on an explicit earnings grid. The wrapper version is 5.3.0, with country model 1.764.6 and core 3.30.1. The stored fixture records a single 40-year-old adult in Texas, filing singly, for 2024. It contains 401 outcomes from zero to \$100,000 earnings and records the wrapper/model versions, certified-bundle manifest, household inputs, tax settings, grid resolution, and content hashes.

The outcome measure is PolicyEngine's household net income with health benefits excluded. It includes some noncash benefits, so it is not described as cash income or a complete fiscal account. The adapter returns the observed grid without interpolation. The optimizer is exact over those supplied choices; it cannot certify unseen cliff locations or an error bound for the unknown continuous schedule between them. Re-running a finer nested grid checks sensitivity to the finite choice set, not statutory completeness.

{{< include generated/household.md >}}

This fixture validates a real model connection and a transparent path to household-level budget analysis. It is not used to estimate national misperception losses. Such an estimate would additionally require credible household-specific beliefs, labor preferences, feasible work choices, treatment of other household members, fiscal valuations, and a provenance-known population dataset. The former population calculation that clipped MTRs and loaded year-only caches is retired explicitly.

## Preferences, learning, and information provision

The retained Cobb-Douglas benchmark gives tax-invariant hours without nonlabor income because income and substitution effects cancel. A positive compensated elasticity alone does not rule out that cancellation. The quasilinear model is not a special case of the displayed homogeneous CES family in earlier drafts, and this note makes no claim that its estimates bound welfare effects under other preferences.

Dynamic learning, information-acquisition costs, participation, and job constraints are omitted. Correcting a worker's beliefs improves that worker's objective under a fixed budget and transfer, but may change tax revenue and others' transfers. Ranking information interventions requires their costs, their effects on behaviorally relevant beliefs, and the chosen social objective. This model does not establish that simplification dominates rate changes.
