# Multi-galaxy morphology implementation plan

Goal: execute the user's staged scientific study in this isolated directory.
Architecture: stream archive images once, retain a compact three-band cache, compute all-band intrinsic morphology; reuse read-only pilot transfer; aggregate by galaxy; deliver a runnable notebook and scientific figures/reports.
Spec: PROTOCOL.md and user's request. Environment: existing phd only.

- [x] A: audit all existing archives against recorded SHA256/size/mtime and FITS metadata; archive_inventory.csv, fits_inventory.csv, galaxy_inventory.csv, selection_audit.csv; preserve hashes of earlier scientific outputs.
- [x] B: numerical validation tests first (analytic circular/elliptical Gaussian, uniform screen invariance, center response, signed negative/empty inputs), original-pilot reproduction, four additional galaxies through transfer/noise. Freeze gate.json before full evaluation.
- [x] C: native intrinsic all-band metrics and g/Ks aperture/center sensitivity; detector-grid references, two strategies, eight paired noise draws; explicit per-case flags.
- [x] D: galaxy bootstrap, viewing-angle scatter, exploratory property associations, held-out subset, zero-SFR/dust audit; focused PSF/depth/distance/spatial-scale checks.
- [x] E: PNG/PDF figures, representative success/weak/reverse cases, scientific report, workshop summary, executed notebook, README, validation and reproduction manifest.

Review focus: radius truncation, zero dust denominators, apparent q versus inclination, noisy nonmonotonic curves, empirical sample balance. Tests and flags must preserve rather than conceal failures. No Git operations: result directory isolation requested; existing experiments and original inputs read-only. No design approval pause: user explicitly requires executing this supplied staged specification.
