# Instrumental assumptions and completed empirical calibration

Verified by artifact inspection on **2026-10-29**. Full evidence, numerical definitions and provenance: [instrument archival review](evidence/INSTRUMENT_ARCHIVE_REVIEW.md).

## ULTIMATE scenarios are assumptions

[Instrument audit](../analysis_results/screen_test_20261026/instrument_audit.md), [parameters](../analysis_results/screen_test_20261026/instrument_parameters.csv), [calibrated provenance](../analysis_results/dr1_calibrated_screen_20261026/instrument_provenance.md) distinguish calculator defaults from measured performance. The sensitivity calculator is pinned to `2187748a40d4207519a8eff0d2a5b6701db8da0d`; original forward-method source to `78dce5ad96038fe7a702d3e2f2b434a2c7d7e8af` in the [source manifest](../analysis_results/screen_test_20261026/sources/pinned_source_manifest.json).

Design defaults include 8.0819 m diameter, 0.277 obscuration ratio, 47.363744 m² collecting area, 0.1 arcsec/pixel, read noise 16 electrons, throughput 0.45, PWV 1.6 mm, airmass 1 and 273 K telescope temperature. Filters are proxies, not measured ULTIMATE transmission curves. Seeing/GLAO median D50 J=0.658/0.508, H=0.624/0.446, Ks=0.588/0.390 arcsec. Gaussian assumptions equate D50 and FWHM; Moffat wings change this relationship. The optimistic 0.2-arcsec scenario is an assumed sensitivity case.

Optical griz uses a separate analyst complementary-imaging scenario held fixed between seeing and GLAO; it is not an optical ULTIMATE capability. Main exposures are one hour per band, seven on-source hours before overhead. Prior experiments investigated 0.25/4-hour, PSF, redshift, resolution, noise and aperture effects. Read-noise accumulation was corrected to Nread×RN², with source/sky/thermal/moon/dark Poisson terms. Flat/persistence, sky subtraction, weather, dithers, fullwell/nonlinearity and resampling floors are not fully modeled. H-band estimated background of about 58,000 electrons/pixel/read leaves operational DIT/fullwell assumptions unverified.

## NGC3256: completed, with historical stages

[Initial raw audit](../analysis_results/hawki_inspection_report.md): 22 exposures, 88 detector images, raw-byte HDU checksums/datasums passed. Raw median provisional FWHM about 0.329 arcsec describes 677 detections, not independent stars. Parser-induced CHECKSUM warnings did not prove corruption; original disk bytes were not rewritten.

[Later empirical report](../analysis_results/ml_feasibility_20261027/hawki/hawki_empirical_calibration_report.md) completed official reduced-image, variance/confidence, archive-calibration and catalogue work. CalSelector returned certified complete associations; the earlier claim that calibration products were missing locally does not mean no archive calibrations exist. No fresh local raw reduction was performed. Reduced compact-candidate median FWHM about 0.3166 arcsec and later same-estimator selected-star median about 0.2942 arcsec use different populations and estimators. Preserve both with their definitions.

## M4-offset: completed empirical sensitivity inputs

[Report](../analysis_results/hawki_m4off_20261028/scientific_report.md), [protocol](../analysis_results/hawki_m4off_20261028/protocol.md), [PSF summary](../analysis_results/hawki_m4off_20261028/PSF_summary.csv), [sensitivity models](../analysis_results/hawki_m4off_20261028/sensitivity_models/README.md).

M4 pawprint and tile are both reduced/resampled products from the same 28 raw IDs, programme 0103.D-0061(C). Header total 1680 s has variable coverage. Tile: 356 primary star measurements, median fitted circularized FWHM **0.3032 arcsec**, 95% spatial bootstrap interval about [0.3005,0.3070], q≈0.874, beta≈3.02. Finite-R2 growth R50/R80≈0.209/0.386 arcsec. Four pawprint planes have medians 0.2925, 0.3200, 0.2946 and 0.2982 arcsec. Measurements repeat identities across products; 276 pairs correspond to 244 distinct Gaia identities. Global paired FWHM change +0.00077 arcsec has CI crossing zero; no robust global sharpening is established.

Subpixel quadrature and fit-window/brightness effects impose additional floors outside bootstrap intervals. Raw source linearity remains unverified despite conservative cuts and removal of flat-core candidates. Wings beyond the measured 2 arcsec are extrapolations; no unique infinite PSF or scattered-light decomposition was measured.

Matched-operator aperture excess over pixel-white scaling, R2/R4/R8/R16: M4 tile≈1.73/2.64/4.60/6.53; NGC3256≈1.41/1.66/1.88/1.98. These include population/coverage/sky differences and confusion; they are not isolated instrumental covariance. R32 noise calibration is **rejected** because of sparse independent support. Five local covariance filters and broader background stress models are sensitivity templates; broad model response discrepancies remain 13–37%. [Model README](../analysis_results/hawki_m4off_20261028/sensitivity_models/README.md).

None of these HAWK-I measurements validates ULTIMATE 0.2-arcsec performance. Absolute external flux/astrometric calibration, per-star raw linearity and confusion-free galaxy-scale noise remain limited. M4 model injection into ML mocks has not been performed and is not required to relabel the completed empirical characterization as finished.
