# Independent review
The positive model's nesting, attenuation bounds, adjoint projection and derivatives were independently reviewed. Off-initialization finite-difference derivatives agree to7e-9 relative error. No target clear template enters `fit()`.

Corrections completed before the final bounded pilot:
- Removed cross-realization warm starts. Every noisy sample uses the same deterministic data-initialized null fit and nested alternative procedure; the earlier pilot process was stopped and this new small pilot restarted. Previous experiments were not rerun.
- Called the statistic penalized MAP-objective improvement, not profile chi-square.
- Corrected mean-versus-median template documentation.
- Removed approximate effective-dof tail probabilities from physical acceptance criteria; local posterior prediction and convergence define the gate. Residual noise expectation is n−2tr(H)+tr(H²), still not an exact nonlinear chi-square law.

Remaining limitations are retained: real-scene optimizer failures; local Laplace approximation; conditional model-family calibration only; incomplete independent stellar-SED coverage; tiny held-out samples; aperture compression; matched-rest-band noise proxies. The reviewer found no blocking positivity/adjoint/derivative error; numerical consistency does not validate physical discrimination.
