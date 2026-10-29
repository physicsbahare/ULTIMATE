"""Generate the scientific handoff from executed tables, without selecting a winner."""
from pathlib import Path
import json
import pandas as pd
from ml_data import OUT, TARGETS


def table(header, rows):
    return '\n'.join(['| '+' | '.join(header)+' |', '| '+' | '.join(['---']*len(header))+' |']+
                     ['| '+' | '.join(str(value) for value in row)+' |' for row in rows])


def run():
    summary=pd.read_csv(OUT/'heldout_summary.csv')
    subset=summary[(summary.condition=='original_noise')&(summary['mode']=='glao')&(summary.bandset=='g_J_Ks')]
    lookup=subset.set_index(['target','model'])
    metrics=[]
    for target in TARGETS:
        metrics.append([target]+[f'{lookup.loc[(target,model),"MAE"]:.5f}' for model in
                       ['median','photometric_ridge','morphology_ridge','ridge','forest']])
    metric_table=table(['Operational target','Constant','Photometry','Morphology','Full ridge','Forest'],metrics)
    gain=pd.read_csv(OUT/'GLAO_ML_gain_summary.csv')
    baseline=gain[(gain.condition=='original_noise')&(gain.bandset=='g_J_Ks')&(gain.model=='ridge')].set_index('target')
    gain_table=table(['Target','Seeing MAE','GLAO MAE','Gain [95% galaxy resampling]'],
        [[target,f'{baseline.loc[target,"seeing_MAE"]:.5f}',f'{baseline.loc[target,"glao_MAE"]:.5f}',
          f'{baseline.loc[target,"mean_gain"]:+.5f} [{baseline.loc[target,"CI_low"]:+.5f}, {baseline.loc[target,"CI_high"]:+.5f}]'] for target in TARGETS])
    correction=pd.read_csv(OUT/'correction_summary.csv')
    correction=correction[(correction.condition=='original_noise')&(correction['mode']=='glao')&(correction.bandset=='g_J_Ks')].set_index(['target','model'])
    correction_table=table(['Target','Uncorrected error','Constant correction','Photometric correction','Ridge correction'],
        [[target,f'{correction.loc[(target,"ridge"),"uncorrected_MAE"]:.5f}']+
         [f'{correction.loc[(target,model),"corrected_MAE"]:.5f}' for model in ['median','photometric_ridge','ridge']]
         for target in ['dR50_g','dR50_Ks','dC_g','dC_Ks']])
    calibration=table(['Target','Covered entire galaxies /22','Mean interval width'],
        [[target,f'{round(lookup.loc[(target,"ridge"),"simultaneous_galaxy_coverage"]*22)}/22',
          f'{lookup.loc[(target,"ridge"),"mean_interval_width"]:.4f}'] for target in TARGETS])
    report=f'''# Preliminary ML feasibility: effective attenuation and morphology correction

Executed on 2026-10-27 in the existing `phd` environment. Original results/data are
read-only. All new outputs are confined here, apart from the separately isolated
authorized DR1 expansion archives. No large neural network or geometry classifier.

## Scientific conclusion

**GO for a larger, carefully validated surrogate-prediction study; no robust GLAO
ML advantage is established by this preliminary benchmark.** Observable g/J/Ks
features predict several operational DR1 paired quantities better than a constant
baseline. Much of the attenuation prediction is already captured by simple
integrated colours. Adding spatial features helps some morphology-bias targets,
but does not improve every target. The median 1-kpc effective-attenuation statistic
is an unsuccessful case: full ridge and forest do not beat the constant baseline.

These are simulation-product prediction results, **not verified physical dust
geometry or dust-mass recovery**. Unknown source-product systematics remain after
excluding the four zero-projected-dust controls. A numerical error smaller than
their residual scale is not an equally precise physical attenuation measurement.

## What was actually executed

- Reused the verified images of all26 previously explored galaxies, five views
  each. Constructed130 seven-target label records and6240 observable feature rows
  across two PSF strategies, three noise conditions and eight draws. Noiseless
  rows are repeated identically eight times to preserve row weighting and forest
  leaf-size conventions; they are not independent noise realizations.
- Excluded four zero-projected-dust objects from every fit/calibration. They are
  a separate challenge set, not relabelled as zero attenuation. The positive-dust
  zero-SFR object is retained: zero SFR is not a dust-free definition.
- Five fixed galaxy folds over the22 remaining objects. In each fold, five other
  galaxies calibrate intervals,12 or13 fit the model, and4 or5 are outer test
  galaxies. All views/draws stay with a galaxy. Hyperparameters were fixed, not
  chosen from these outer tests. This is exploratory development CV; no object
  in the new final-evaluation partition was scientifically inspected or fitted.
- Compared training median, photometric ridge, morphology ridge, full ridge and
  a shallow80-tree random forest. Fitting-only imputers/scalers and target
  standardization prevent test information entering preprocessing. Ridge alpha10;
  forest depth4/minimum20rows per leaf; forest uses shared standardized multi-target
  splits. `train_test_provenance.json` lists exact features and split IDs.
- Tested noiseless, original exact-moment noise, and equal noise across strategies.
  Equal-noise pixels use the maximum seeing/GLAO variance with paired innovations.
  This separates the PSF comparison from differing added-noise variances.
- Re-rendered original dusty noise properties match the previous verified tables.
  g-only features and predictions are identical between strategies. Four integrity
  tests include disjoint galaxy roles, observable feature allowlists and a direct
  perturbation showing test truth cannot change predictions or interval widths.

## Inputs and target definitions

Models receive only measured dusty-image properties: aperture Jy flux, R50,
concentration, raw asymmetry, apparent q, central light fraction, integrated colours
and inner/outer colour gradients. They receive no clear map, physical dust map,
stellar mass/SFR, true inclination, galaxy ID, target or noise-realization identifier.
IDs are used only for partitioning/scoring. Total flux is an observable, but at
one fixed distance it can exploit a sample-specific luminosity prior; success
does not demonstrate population-independent dust inference.

`A_g` and `A_Ks` are -2.5log10(sum dusty/sum clear) within the fixed12-kpc aperture.
`A_g_p50_1kpc` is the median -2.5log10(smoothed dusty/smoothed clear), using1-kpc
Gaussian FWHM, positive finite flux, clear >1e-4 of its smoothed peak and R<12kpc.
Negative valid effective attenuation is retained. These are effective broadband
statistics, not optical depth. `dR50` and `dC` use native dusty-minus-clear pairs,
with C=5log10(R80/R20). Known center/distance and fixed circular aperture are
idealizations inherited from the validated study. No segmentation/orientation
criterion was tuned to improve held-out errors.

## Held-out performance

Equal-galaxy MAE, original noise, GLAO proxy, g/J/Ks inputs. Attenuation units are
mag; R50 differences are kpc; concentration is dimensionless. Every entry has22
held-out galaxy contributions; views/pixels/noise draws are not independent objects.

{metric_table}

The photometric baseline uses g flux plus integrated colours, without spatial
morphology features. It beats full ridge for integrated g attenuation (0.08877 versus
0.09720mag). Full ridge improves Ks R50-bias prediction over the colour baseline
(0.04928 versus0.06881kpc). These comparisons use the same folds; all signed paired
effects and galaxy-resampling intervals are in `paired_model_comparisons.csv`.
They are not a model-selection exercise identifying a final deployable model.

## Does GLAO help ML?

Predefined gain is seeing MAE minus GLAO MAE, averaged within galaxies first.
The full-ridge primary comparison is:

{gain_table}

**Every full-ridge primary interval includes zero.** Forest primary intervals
also include zero for all seven targets. Extra NIR information shows larger
improvements than the PSF change. g-only versus g/J/Ks uses1hour per band, hence
different total telescope allocations (1 versus3hours before overheads); it is
an information ablation, not an equal-time efficiency forecast.

The noiseless and equal-noise comparisons retain weak/mixed resolution effects;
there is no universal monotonic benefit. The noiseless forest g R50 target even
worsens under the narrower NIR PSF. No multiple-testing-adjusted significant
advantage is claimed. The5000-resample intervals condition on the fitted models,
folds and selected galaxies: overlapping training sets and training-set uncertainty
are not fully captured. The sample is not volume representative.

## Morphology correction

Subtract predicted native dust bias from the observed dusty morphology and score
against native clear morphology. This tests whether a numerical correction helps;
the PSF/noise error remains, and no clear image is reconstructed. Galaxy-mean MAEs:

{correction_table}

Simple constant correction already helps substantially. Incremental benefit over
that baseline, the colour baseline and all unfavorable galaxies must remain
visible; `correction_summary.csv` reports per-target signs and uncertainty. This
benchmark cannot establish an unbiased correction for arbitrary real galaxies.

## Uncertainty calibration and OOD behavior

Nominal80% split-conformal diagnostic: five calibration-galaxy scores, each the
maximum absolute residual over all its views/draws, give one simultaneous bound
per target. The required finite-sample order is ceil(6*0.8)=5, the maximum score.
Full ridge shows the following empirical entire-galaxy coverage:

{calibration}

The g R50 target covers only15/22 galaxies, and integrated g attenuation16/22;
this is not demonstrated80% population calibration. Intervals are often broad.
Finite selected samples, OOD objects and unknown physical-label errors prevent
unqualified coverage guarantees. Noise-draw prediction SD is separately saved;
it is not substituted for between-galaxy or model uncertainty. The method follows
the split-calibration framework described by
[Angelopoulos & Bates](https://arxiv.org/abs/2107.07511); its exchangeability premise
is not established for this selected simulation sample.

The deliberate high-mass-quartile challenge holds out6 galaxies and fits only
the16 lower-mass objects. Full-ridge g concentration-bias MAE worsens to0.7675,
versus0.2345 in grouped CV; Ks R50 MAE is0.0554 versus0.0493. The four source-null
controls give Ks R50-bias MAE0.1672, much worse than CV. Physical metadata define
these diagnostics but never enter X. `OOD_summary.csv`, exact split IDs and
observable-space nearest-training distances preserve the failure cases.

## Physical-label and aperture uncertainty

The four controls have median integrated pair residuals0.1214mag in g and0.0205mag
in Ks despite zero projected field dust. Their maximum view-level |dR50| values
are0.0311 and0.0392kpc. No universal offset is subtracted. These controls are a
warning, not a validated transferable error distribution. Excluding them is
insufficient to prove the remaining22 labels are physically exact.

Changing the target aperture from12 to30kpc changes the native dust-bias label
by a median galaxy-mean absolute0.2436kpc in g R50 and0.0494kpc in Ks R50 across
the22 fitting-eligible galaxies. These are comparable to ML errors and far larger
than the primary GLAO gains. Center offsets and concentration sensitivities remain
tabulated in `label_policy_uncertainty_summary.csv`; fixed-prediction stress under
alternative definitions is explicitly a task-definition change, not Gaussian
label noise. A stable scientific aperture/segmentation policy is a prerequisite
for interpreting better prediction as better physical correction.

## HAWK-I calibration and empirical sensitivity

Official ESO reduced products and their variance/confidence maps exist for the
same observations. We obtained small target-centered Jan6 science/variance/weight
cutouts (64.18MiB retained;128.36MiB total including a corrected initial cutout),
checked checksums and aligned WCS grids, and executed image-level fits and masked
sky/aperture-noise measurements. Local raw frames are complete for the22 archive
science exposures. Certified calibration associations exist, but local master
calibrations and EsoRex are absent; an unnecessary incomplete raw reduction was
not attempted. See [the empirical calibration report](hawki/hawki_empirical_calibration_report.md).

The103 accepted reduced compact-source candidates have median FWHM0.3166arcsec,
Moffat beta4.753, q0.820 and circularized D50=0.3533arcsec. Candidate/field scatter
and analytic growth-curve extrapolation are explicit; stellar identities and
absolute external astrometric/photometric validation are not assumed. Adjacent
background correlations are0.2753/0.2932. At32pixel aperture radius, noise is3.42
times sigma_pixel sqrt(N), and2.01 times the propagated diagonal-variance prediction.
Thus pixel variance alone is inadequate for larger-scale surface-brightness work.

A small catalogue follow-up finds9 quality-selected stellar matches to2MASS:
median radial offset0.121arcsec (RMS0.169arcsec), and HAWK-I minus colour-transformed
2MASS Ks median-0.0558mag with robust scatter0.1390mag (RMS0.2429mag, outlier retained).
This recomputes consistency using the same reference system that the pipeline
used; it is not an independent astrometric/photometric calibration or a precision
zeropoint validation. Exact matching, aperture correction and colour conventions
are documented in the HAWK-I report and saved match table. The actual associated
PHOTCAL table uses0.03J+0.97Ks; the release description instead prints an H-based
term. Both residual calculations are retained and the actual calibration-file
formula is used here. The nine quality stellar matches have median FWHM0.2935arcsec
and beta3.7415, illustrating selection sensitivity relative to all103 compact
sources. The executed empirical stress retains its recorded full-sample beta4.753;
it is not silently retuned to the smaller stellar subset.

An executed **post-protocol** sensitivity uses the measured beta for Ks wings while
retaining provisional seeing/GLAO D50 values. A separate local covariance stress
matches the two adjacent correlations with a unit-variance separable3pixel filter.
Measured longer-scale sky correlations, anisotropy, field variation and larger
aperture noise are not reproduced. It is not a calibrated HAWK-I or ULTIMATE noise
model, and real ADU amplitudes are not transferred to the simulated electron model.
`empirical_stress_summary.csv` records all seven targets/models and retains mixed
or adverse outcomes. Any isolated positive interval is exploratory, with no
multiple-comparison correction; it does not override the frozen primary result.

## Expansion and publication readiness

The exact120-galaxy metadata-only manifest is frozen:86development (all26 old plus
60new),14validation,20completely untouched final evaluation. All94 new archives
passed official DR1 byte-range/size preflight:60,164,124,583bytes (56.032GiB).
The resumable background download is running; consult the timestamped
`expansion/acquisition_status.json` for actual verified counts rather than treating
120 as an achieved download count. Archive CRC/tar checks do not inspect final-test
scientific images. Every transfer chunk enforces100GiB free disk plus safety margin.

Official selection metadata lack dust mass and morphology classes; broad mass/
activity stratification and explicitly qualified gas/size proxies were used.
The selection probabilities and unavailable dimensions are documented, not invented.
No new galaxy image has entered this benchmark. Future validation/final partitions
must stay separate from training, hyperparameter choice, calibration and feature
design; resolve that workflow before opening their labels.

**Workshop-ready with negative and positive results together.** Suggested figures:
01 (baselines),03 (bands versus resolution),05 (coverage/OOD),06 (correction), plus
HAWK-I reduced PSF/noise panels. A safe abstract update is “learning effective
attenuation statistics and morphology corrections from radiative-transfer mocks,”
not unique3D dust geometry. The prior false positives and geometry-model failures
remain unchanged.

**A dedicated paper needs more than this pilot:** complete acquisition, improve
source-product physical-null calibration and aperture robustness, increase the
independent training sample, establish held-out uncertainty/OOD behavior, include
realistic field-dependent PSF/sky/covariance systematics and actual observer-filter
synthetic photometry, then perform one frozen final evaluation. Dust-dependent
morphology itself overlaps the larger
[TNG50-SKIRT atlas morphology study](https://arxiv.org/abs/2605.20886); distinctive
novelty should be validated instrumental transfer and defensible observational
prediction, not rediscovery of an atlas trend. No universal ULTIMATE gain is claimed.
'''
    (OUT/'scientific_report.md').write_text(report)
    workshop=f'''# Workshop results: two modest ML applications

-22 independent fitting-eligible galaxies;4 zero-projected-dust source controls
kept out of fitting. All26 remain development objects. Five galaxy folds,
galaxy-calibrated intervals, no view/noise leakage, fixed shallow models.
-Integrated g effective-attenuation MAE: full ridge0.0972mag; simple colours0.0888;
constant0.2212. Median1-kpc spatial attenuation does not beat the constant baseline.
-Ks dust-induced R50 MAE: full ridge0.0493kpc; colours0.0688; constant0.0996.
-Ks native-clear R50 error after correction: raw0.1765kpc, constant-corrected0.0977,
ridge-corrected0.0648. Improvement is conditional, not unbiased physical recovery.
-No robust primary GLAO ML gain: ridge Ks R50 error reduction0.00018kpc,
95% galaxy-resampling interval[-0.00095,0.00157]. Extra NIR information dominates
the seeing/GLAO change in this small benchmark.
-Nominal80% ridge intervals cover only15/22 entire galaxies for g R50. Source-null
Ks R50 challenge error0.1672kpc; aperture changes rival prediction error.
-Official reduced HAWK-I cutouts:103 accepted compact sources, medianFWHM0.317arcsec,
beta4.75; adjacent sky rho~0.28–0.29, large-aperture excess noise measured.
Empirical-informed stress tests are executed but are not ULTIMATE calibration.
-120-galaxy partition frozen86/14/20;94 downloads preflighted56.03GiB, background
acquisition in progress. Use live status for verified count; final20 images sealed.

Show Figures01,03,05,06 and `hawki/reduced_noise.png`. Keep the source-product
residuals, fixed12-kpc aperture and matched-rest-band/provisional instrument
assumptions on the results slide. No unique geometry, mass or real0.2arcsec claim.
'''
    (OUT/'workshop_results.md').write_text(workshop)
    print('Scientific report and workshop summary generated from executed results.')


if __name__=='__main__':run()
