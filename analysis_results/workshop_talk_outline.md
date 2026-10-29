# Workshop talk: 10-minute draft

Eight slides, 600 seconds total. PDF: `workshop_10min.pdf`. All measured values derive from the executed local analysis; forward modelling remains planned.

## 1. Beyond the Foreground Screen — 45 seconds

Frame the research question. These are preliminary results, not a trained dust-geometry model. Establish the distinction between information in ideal images and information recoverable in observations.

## 2. First establish a reproducible measurement — 60 seconds

Integrated attenuation is a ratio of full-frame sums; the spatial statistic uses a different aperture. Intensities are MJy/sr, dust columns M☉/pc², grid 100 pc. Explain the relative 10⁻⁴ threshold in both dust-free bands. Negative attenuation is retained; the twin exists only in simulation.

## 3. The projection changes across viewing directions — 90 seconds

Explain rows: effective g attenuation and projected dust column. Every view uses the same physical field and colour scale. Red/blue retain negative attenuation; colour limits clip display only. Orientations are related views, not five galaxies. A column density is a line-of-sight integral; it does not specify where the dust sits relative to the stars.

## 4. Integrated attenuation and association depend on view — 90 seconds

Read the g range 0.231–0.604 mag and Ks range 0.0066–0.0831 mag. g association stays strong under the pilot mask, while Ks varies greatly. The right panel spans 27 analyst choices per view: bin sizes 0.5/1/2 kpc, thresholds 10⁻⁵/10⁻⁴/10⁻³, radii 10/20/30 kpc. Shading is an analysis-choice range, not error bars or population uncertainty.

## 5. Ks is not a universal monotonic dust tracer — 90 seconds

Focus on O2: Ks rho −0.076 compared with positive O3–O5 values. Do not interpret it as dust causing negative extinction: effective attenuation incorporates scattering, and faint Monte Carlo fluctuations matter when Ks attenuation is small. Keep negative values. Correlations are descriptive and spatially correlated; no independent-pixel p-values. Radius alone does not fully explain the strong optical association, but that is not proof of causal geometry recovery.

## 6. Real-data anchor: raw HAWK-I/GRAAL Ks observations — 75 seconds

Show the separately supplied raw preview if time permits. The accepted widths are from 677 compact-source Moffat fits, repeated detections, not unique confirmed stars. Raw gradients and flat-field artifacts remain. Total nominal duration 673.2 s is not uniform coverage. No local reduced stack/calibrations. This is an empirical imaging anchor, not dust-free truth or a 0.2-arcsec image.

## 7. Next: a small forward-modelling feasibility test — 90 seconds

Instrument numbers are design references from the project instrument plan and WFI design slides, not guarantees. Match optical/NIR PSFs before forming colours. Select distance and resolution honestly, then calibrate sky, throughput, read noise and exposure assumptions. Keep dust-free twins for evaluation only. Planned test is not yet an executed recovery result.

## 8. What is established — and the next decision — 60 seconds

Close on the actual result and request scientific feedback: which distance regime and geometry target matter most? More independent galaxies are needed before generalization. A projected dust map cannot alone identify vertical thickness, clumping or star–dust separation. No unique 3D recovery or ML accuracy is claimed.

## Backup material

Use `figures/hawki_raw_preview.*` for the labelled raw detector view, `hawki_psf_diagnostics.*` for fit examples, and `tng_orientation_summary.csv` for the exact table. Main figures are also available independently in PNG/PDF. Add presenter affiliation and workshop session details before presenting; no affiliation was inferred. Instrument references and assumptions are documented in `next_experiments.md`.