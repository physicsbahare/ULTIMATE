# Beyond the Foreground Screen: what ML and NIR resolution recover

**120 verified TNG50-SKIRT DR1 galaxies; frozen 86/14/20 partition; one final evaluation.** Models fit 74 positive-dust development galaxies, calibrate on13 validation galaxies, and evaluate on16 final primary galaxies plus4 separately retained source controls. Every galaxy keeps all views and noise draws together.

| Final operational target | Constant MAE | Recommended GLAO MAE |
| --- | --- | --- |
| Integrated g attenuation | 0.3003 mag | 0.0741 mag |
| Integrated Ks attenuation | 0.0594 mag | 0.0124 mag |
| Ks dust-induced ΔR50 | 0.1282 kpc | 0.0799 kpc |
| Ks dust-induced ΔC | 0.1521 | 0.0887 |

Photometry already supplies much of the predictive information. The incremental integrated-g gain over photometric ridge and the Ks radius-bias gain over the constant have paired intervals spanning zero. The spatial median improves modestly, with a large error tail. Some more complicated models lose to photometry.

**No robust positive GLAO gain in dust-bias prediction is demonstrated.** Improved resolution does preserve morphology: corrected Ks size MAE relative to the native clear reference improves from0.1210kpc seeing to0.0861kpc GLAO, while the predicted dust bias itself has no significant resolution gain.

These are signed DR1 paired-product predictions, not calibrated physical attenuation. Zero-projected-dust controls retain approximately0.12mag g offsets; concentration is aperture/center sensitive. HAWK-I informs instrumental nuisance tests, not dust truth or a real0.2arcsec ULTIMATE PSF. Fixed-rest-band mocks are not validated observer-frame forecasts.

**Publication message:** a transparent, interpretable feasibility benchmark with baselines, source controls and a separation of morphology transfer from physical inference. Source-product reconciliation, observer-frame instrumental calibration and independent domain tests remain necessary before physical dust or unique3D geometry claims. The final20 has been used once; supplementary models remain validation-only.

See [the verified handoff](project_continuation_report.md) and [canonical scientific report](../ml_expanded_20261028/scientific_report.md). Main figures and executed notebooks are linked there.
