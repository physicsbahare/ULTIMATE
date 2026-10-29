# Beyond the Foreground Screen — workshop results

**120 verified galaxies;74 development fits,13 calibration galaxies;16 untouched positive-dust final galaxies plus4 final source controls.** Frozen86/14/20 assignments, grouped5-fold development selection, one final evaluation; four noise draws×five correlated views per galaxy.

Operational DR1 contrasts, **not yet calibrated physical attenuation**. Four exact-zero-dust source controls retain≈0.12-mag g offsets; no global subtraction. No unique3D geometry recovery.

| target | constant | phot_seeing | seeing | GLAO |
|---|---|---|---|---|
| A_g | 0.3003 | 0.0794 | 0.0734 | 0.0741 |
| A_g_p50_1kpc | 0.0522 | 0.0497 | 0.0441 | 0.0441 |
| dR50_Ks | 0.1282 | 0.0992 | 0.0777 | 0.0799 |
| dC_Ks | 0.1521 | 0.1174 | 0.0887 | 0.0887 |

Values are equal-galaxy MAE. Magnitudes/kpc/dimensionless concentration as appropriate. Recommended models were selected before final access, not by final scores. Constants and photometry remain essential baselines. Paired95% gain intervals are in `workshop_key_numbers.csv` and the gain figure.

None of the eight recommended-model final paired GLAO-gain intervals excludes zero on the positive side. Intervals support adverse effects for dR50_g.

TaskB corrections and PSF transfer must be separated: see `scientific_report.md` and native-clear corrected errors. Concentration is center-sensitive; a0.5-kpc offset changes ΔC materially. GLAO preserving morphology does not establish identification of individual dust structures.

**Slides:** `figures/model_and_observing_strategy_comparison.png`, `paired_GLAO_gains.png`, `prediction_vs_atlas_target.png`, `learning_curves.png`, `representative_success_and_failure_images.png`. PDF counterparts are available.

**Honest conclusion:** workshop-ready as a conditional benchmark with negative results and source controls. Physical-dust/ULTIMATE publication requires source-label calibration, realistic observer-frame/instrument validation and independent domain-transfer tests. HAWK-I informs nuisance tests, not dust truth or a calibrated ULTIMATE PSF. The final20 is now used and must not be retuned upon.
