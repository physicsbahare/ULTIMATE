# Proposed workshop result, grounded in executed tests

**Main statement:** “We can detect spatial optical/NIR colour structure in a static, structured SKIRT galaxy under an instrument-informed ULTIMATE-like noise model. But spatial colours alone do not reject uniform dust: the same test detects gradients in a uniform-screen control because its stellar populations vary. After marginalizing over external population templates, screen preferences depend on the assumed template/discrepancy budget, and some known uniform controls are falsely rejected. We therefore do not yet claim mixed dust geometry recovery.”

**GLAO statement:** “Using the sensitivity calculator's median design D50 values, narrower NIR PSFs improve a known-population separation bound by about 2–12% over z=0.1–1. This is conditional on knowing the stellar scene; it is not the significance of detecting dust from observations. We have not demonstrated a robust GLAO improvement in the fully population-marginalized screen test.”

**Method statement:** “The physical galaxy size, luminosity, stellar populations and dust are held fixed. Only distance, wavelength mapping, PSF, sampling and exposure-level detector statistics change. No Sérsic replacement, intrinsic size evolution or ML training is used.”

**Instrument qualification:** “This is a calculator-informed design experiment, not a finalized ULTIMATE performance prediction. Broadband spectral interpolation, provisional optical/de-tector settings, the known-sky baseline and the unknown final PSF/filter curves remain material limitations.”

Suggested three evidence slides:

1. `figures/synthetic_observed_images.*`: static structured transfer, matched within-band display stretches.
2. `figures/screen_evidence_with_null_controls.*` plus `model_discrepancy_robustness.*`: model comparison with the null controls visible.
3. `figures/glao_oracle_upper_bound.*`: explicitly labelled conditional bound, followed by the concrete need for population-complete null recovery and validated spectral/filter synthesis.

Do not use colour-gradient χ², profile χ² reduction or the known-population separation as a unique dust/3D-geometry detection significance. The legacy authenticated atlas link has not been verified as DR2.
