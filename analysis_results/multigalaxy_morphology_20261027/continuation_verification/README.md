# Continuation verification and source-null sensitivity

The requested multi-galaxy study was already present on inspection. Its executed
notebook, modules, tables, reports and figures were preserved. This continuation
adds fresh numerical work and provenance checks without restarting the study.

## Executed verification

- Current SHA256 and byte lengths match all 26 recorded archives. The 25 additional
  files also match the downloader's verified SHA256, gzip-CRC and tar-payload records.
  This preserves the recorded CRC evidence; a new redundant full decompression
  of all extra archives is not claimed.
- All 795 files in the primary study manifest, and all 289 earlier scientific
  result files, match their recorded hashes before and after the audit.
- The existing 10 unit tests pass, including analytic morphology, uniform-screen
  invariance, signed-pixel handling, paired-validity rules, corrupted-gzip rejection
  and legacy-import isolation.
- Independently reconstructed absolute errors from `observed_morphology.csv`,
  using independent clear/dusty noise and joint strategy validity. Per-galaxy
  gains agree with saved values to 9.98e-17.
- Re-executed the O1 end-to-end seeing/GLAO simulations for 294866, 167418,
  626287, 535051 and 638950, with all three bands, scenes and eight noise draws.
  The 840 resulting morphology rows reproduce the saved calculations within
  numerical/CSV precision. Maximum absolute differences include flux units and
  should not be interpreted as morphology errors.
- Independently recomputed 20 native g/Ks R50 measurements by radial-shell
  integration, rather than the primary pixel-order helper: exact radius agreement.
- Reopened actual O1 g FITS members in two development archives; header, unit,
  pixel scale, raw-member hashes and cropped cache arrays agree. This is a raw-FITS
  spot check; completeness of all 6240 members is supported by the original
  inventory and unchanged archive hashes.
- Fresh 100000-draw aggregate Poisson plus 60-read Gaussian read-noise checks per
  band reproduce analytic variance to ratios 0.99603, 0.99921 and 1.00030 (g/J/Ks).
- The primary notebook remains executed: 12 code cells, no error outputs and
  11 embedded figures matching saved PNGs. The supplementary notebook was also
  executed top to bottom, independently recomputing native and accuracy statistics.
  Kernel startup required local socket permission; no packages were installed.
- Visually inspected unchanged Figures 02, 03, 05, 09 and 11 in this continuation.
  Notebook HTML is structurally exported; a separate browser rendering was not checked.

## New sensitivity calculation

The four objects with zero field projected dust are **not** subtracted as a
universal calibration. We compare the frozen all-26 primary results to descriptive
results excluding them. Their exclusion does not resolve source-systematic
uncertainty, restore sample representativeness or define a new primary sample.

Median of galaxy-mean dusty-minus-clear R50, fixed R<12-kpc aperture, native rest
bands; brackets are 95% galaxy-bootstrap intervals with 5000 resamples:

| Sample | LSST g, kpc | 2MASS Ks, kpc |
|---|---:|---:|
| All 26, unchanged primary | +0.4003 [0.1704, 0.5459] | +0.1239 [0.0827, 0.1702] |
| Nonzero projected dust, 22 | +0.5007 [0.3590, 0.5890] | +0.1388 [0.1094, 0.1820] |

The positive median size contrast is retained. Galaxy 294866 remains an opposite-sign
outlier. None of these intervals includes uncertainty in the source radiative-transfer
products, aperture policy, selection design or instrument assumptions.

Conditional Ks mean error reduction, seeing minus GLAO, at fixed-rest-band z=0.1,
1 h per band, independent clear/dusty observation noise:

| Target and metric | All 26 gain [95% galaxy bootstrap] | Nonzero-dust 22 gain [95% galaxy bootstrap] |
|---|---:|---:|
| Dusty R50 preservation, kpc | 0.04113 [0.02493, 0.05880] | 0.02810 [0.01601, 0.04346] |
| Dusty concentration preservation | 0.17686 [0.13928, 0.21350] | 0.15970 [0.12208, 0.19839] |
| Dusty-minus-clear R50 recovery, kpc | 0.00339 [0.00063, 0.00675] | 0.00297 [0.00003, 0.00665] |
| Dusty-minus-clear concentration recovery | 0.00958 [-0.00255, 0.02085] | 0.00849 [-0.00470, 0.02122] |

Morphology preservation is the stronger instrumental result. Dust-specific R50
gains are small and the concentration-recovery interval crosses zero in both
samples. Eight science noise draws per scene cannot establish detailed tail
probabilities. The asymmetry estimator sensitivity and occasional adverse q
results remain in the primary report; they are not removed by this supplement.

## Scientific assessment

**Workshop: usable with caveats.** Present galaxy-level sign reversals, wavelength
dependence and conditional Ks size/concentration preservation together with the
zero-projected-dust controls. The five directions remain repeated measurements,
not independent galaxies. Fifteen galaxies have substantial primary-aperture
truncation in at least one g/Ks scene/view. Filter identities, provisional PSFs,
rest-band distance degradation and the absence of exact observer-frame Ks
photometry must remain explicit.

**Paper: promising foundation; not yet a validated ULTIMATE forecast.** Resolve
the source-product residuals, quantify aperture/systematic sensitivity and validate
actual observer-filter/PSF/sky assumptions before making strong instrumental or
physical attribution claims. A primary-literature check confirms direct overlap
with [Bokona Tulu et al. (2026)](https://arxiv.org/abs/2605.20886), who already
study dust-dependent nonparametric morphology across the larger atlas. Distinctive
novelty would need to come from validated instrumental information transfer.
The [DR1 methodology](https://arxiv.org/abs/2401.04224) and
[Pastrav et al. (2013)](https://arxiv.org/abs/1301.5602) remain relevant references.
Only those existing references were checked; no science datasets were downloaded.

## Reproduction and output locations

Use the existing environment, from `/home/bahareh/ULTIMATE`:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl
export PYTHONDONTWRITEBYTECODE=1
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multigalaxy_morphology_20261027/continuation_verification/verify_existing_study.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multigalaxy_morphology_20261027/continuation_verification/check_noise_moments.py
JUPYTER_RUNTIME_DIR=/tmp/ultimate-jupyter-continuation IPYTHONDIR=/tmp/ultimate-ipython-continuation /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multigalaxy_morphology_20261027/continuation_verification/execute_verification_notebook.py
```

The supplementary notebook needs local Jupyter sockets. Its calculations write
only the supplementary tables. The first script rereads compressed archive bytes
for SHA256; it does not fully extract archives. A finite seeded bootstrap depends
on input order: the independent audit explicitly sorts galaxy IDs to reproduce
the original sample ordering, after diagnosing a 0.00263-kpc endpoint difference
from using inventory order. This does not alter the original interval or protocol.

- [Primary scientific report](../scientific_report.md)
- [Primary executed notebook](../ULTIMATE_multigalaxy_morphology.ipynb)
- [Workshop summary](../workshop_summary.md)
- [Complete reproduction instructions and output map](../README.md)
- [Supplementary executed notebook](independent_verification.ipynb)
- [Fresh verification receipt](verification_receipt.json)
- `fresh_archive_integrity.csv`, `fresh_raw_FITS_spotchecks.csv`: source evidence.
- `five_galaxy_fresh_replay.csv`, `independent_radial_shell_R50.csv`: execution checks.
- `independent_native_and_null_sensitivity.csv`: new native sensitivity values.
- `independently_recomputed_galaxy_gains.csv`,
  `independent_accuracy_and_null_sensitivity.csv`: independent observing calculations.
- `fresh_noise_moment_validation.csv`: fresh radiometric/noise checks.
- `execution.log`, `notebook_execution.log`, `unit_tests.log`: execution records.
