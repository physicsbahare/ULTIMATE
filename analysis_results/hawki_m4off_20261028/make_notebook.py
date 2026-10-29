from pathlib import Path
import nbformat as n
O=Path(__file__).resolve().parent
md=n.v4.new_markdown_cell;code=n.v4.new_code_cell
cells=[md('''# M4-offset HAWK-I/GRAAL empirical calibration

## Findings
The tile median Moffat FWHM is **0.3032 arcsec**. Identical-star comparison gives **+0.00077 arcsec** tile minus pawprint, with a spatial interval crossing zero. Crowding materially affects large-aperture noise. These products support bounded observational sensitivity experiments, not a unique instrumental calibration or dust truth.

## Context and methods
This executed evidence notebook reads completed measurements and independently reruns the integrity/numerical checks. The full source extraction was executed by the scripts and logs beside it. It does not retrain ML or open final-test science.

Assumptions: common28 raw exposures; already resampled stacks; signed finite-R2 growth curves; spatial rather than pixel bootstrap; no proof of each raw core's linear history. Full methods and official calibration links are in `protocol.md` and `scientific_report.md`. Use the existing phd Python environment.'''),code('''from pathlib import Path
import sys, json, subprocess
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, Image
O=Path.cwd()
if not (O/'PSF_summary.csv').exists():
    O=O/'analysis_results/hawki_m4off_20261028'
assert (O/'PSF_summary.csv').exists()
plt.rcParams.update({'figure.figsize':(10,4),'font.size':10})
s=pd.read_csv(O/'science_star_table.csv')
summary=pd.read_csv(O/'PSF_summary.csv')
pairs=pd.read_csv(O/'matched_stars_primary.csv')
assert pairs.gaia_id.nunique()==244
'''),md('## Data and integrity\nOriginal and small ancillary product provenance is recorded with hashes. All five science planes remain represented.'),code('''provenance=pd.read_csv(O/'fits_provenance.csv')
display(provenance[['extension','extname','mode','GRAAL','BUNIT','PHOTSYS','QCFLAG_digits','scale_arcsec','wcs_roundtrip_max_pixel']])
result=subprocess.run([sys.executable,str(O/'verify_results.py')],capture_output=True,text=True)
assert result.returncode==0,result.stderr
verification=json.loads((O/'verification.json').read_text())
display({k:v for k,v in verification.items() if k not in ['environment','independent_synthetic_fit']})'''),md('## Spatial PSF and fit distributions\nIntervals describe conditional medians across spatial cells. Detector2 has only four strict wing probes. Nonlinearity and quadrature floors are additional systematics. A synthetic0.22-arcsec, q0.8 case has a0.058 q error, showing optimizer/undersampling sensitivity.'),code('''display(summary[['field','n_stars','n_wing_reliable','fwhm_arcsec_median','fwhm_arcsec_median_CI95_lo','fwhm_arcsec_median_CI95_hi','q_median','beta_median']].round(4))
good=s[s.primary_star]
fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,col,label in zip(axes,['fwhm_arcsec','q','beta'],['FWHM (arcsec)','Axis ratio q','Moffat beta']):
    groups=list(good.groupby('field'))
    ax.boxplot([g[col].to_numpy() for _,g in groups],tick_labels=[f for f,_ in groups],showfliers=False)
    ax.set_ylabel(label);ax.tick_params(axis='x',rotation=35)
plt.show()'''),code('''display(Image(filename=str(O/'figures/spatial_PSF_maps.png')))
display(Image(filename=str(O/'figures/spatial_shape_and_wings.png')))'''),md('## Identical stars across products\nThe 276 rows represent244 identities. Paired changes share photons; these are not independent observing realizations. Spatial intervals and estimator floors discourage precision global-processing claims.'),code('''changes=pd.read_csv(O/'paired_changes.csv')
d=changes[changes.quantity=='delta_fwhm_arcsec'].copy()
display(d[['field','n_unique_stars','median','cluster_lo','cluster_hi']].round(6))
fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
y=np.arange(len(d));ax.errorbar(d['median'],y,xerr=np.vstack([d['median']-d.cluster_lo,d.cluster_hi-d['median']]),fmt='o',capsize=4)
ax.axvline(0,color='gray',ls=':');ax.set(yticks=y,yticklabels=d.field,xlabel='Tile − pawprint FWHM (arcsec); 95% spatial bootstrap')
plt.show()'''),md('## Finite empirical wings\nCircular EE is relative to2arcsec. Cleaner detected neighbours and annular-scatter cuts reduce, but do not remove, unresolved-star contamination. Moffat tails beyond this radius are fitted extrapolations.'),code('''display(Image(filename=str(O/'figures/EE_spatial_bootstrap.png')))
display(Image(filename=str(O/'figures/empirical_encircled_energy.png')))
display(pd.read_csv(O/'fit_window_summary.csv').round(5))
quad=pd.read_csv(O/'quadrature_sensitivity.csv')
display(quad[['truth_FWHM_arcsec','truth_beta','truth_q','delta_FWHM_arcsec','fractional_FWHM_bias']].round(5))'''),md('## Finite-growth model sensitivity\nA core+Gaussian halo fits finite outer light missed by the single Moffat. It is a phenomenological stress model; detector2 has sparse support and a boundary optimum. Halo fractions are not uniquely measured physical flux fractions.'),code("""display(Image(filename=str(O/'figures/growth_curve_model_sensitivity.png')))
growth=pd.read_csv(O/'sensitivity_models/finite_growth_model_grid.csv')
display(growth[growth.best][['field','halo_FWHM_arcsec','halo_fraction_extrapolated_total','finite_EE_RMS','n_clean_wing_stars']].round(4))"""),md('## Background covariance and crowding\nThe same-estimator comparison is between different scenes, not matched depths. R32 void apertures are too sparse for calibration. Region intervals omit mask/sky systematics and do not count overlapping centers as independent.'),code('''display(pd.read_csv(O/'same_operator_noise_summary.csv').round(3))
display(Image(filename=str(O/'figures/NGC3256_same_operator_noise.png')))
u=pd.read_csv(O/'aperture_noise_uncertainty.csv')
display(u[(u.field=='tile0')&(u.kind=='grid')][['radius_pixels','n_regions','n_geometrically_nonoverlapping_lower_bound','median','p16','p84','median_region_boot_CI95_lo','median_region_boot_CI95_hi','calibration_accepted']].round(3))
display(Image(filename=str(O/'figures/crowding_and_aperture_reliability.png')))'''),md('## Model checks and handoff\nUse local-correlation kernels separately from the broader total-background mixture. The latter has retained13–37% response discrepancies and includes confusion. Amplitude and ULTIMATE instrument specifications require separate calibration.'),code('''checks=pd.read_csv(O/'sensitivity_models/local_noise_simulation_checks.csv')
checks['absolute_difference']=abs(checks.realized-checks.predicted)
display(checks.groupby('field').absolute_difference.max().round(5))
models=json.loads((O/'sensitivity_models/noise_family.json').read_text())
display(pd.DataFrame([{'field':m['field'],'maximum_response_misfit':m['max_fractional_response_error'],'scope':m['calibration_status']} for m in models]))
assert not good.flat_core_flag.any()
assert summary.n_stars.sum()==965
print('All notebook checks passed. Previous ML frozen-artifact receipt:',verification['previous_ML_freeze_receipt_sha256'])'''),md('''## Interpretation
Measured HAWK-I core quality spans roughly0.29–0.32arcsec. No robust global same-star processing shift is demonstrated. Spatial ellipticity and wings should be preserved jointly. Background variance is strongly aperture- and mask-dependent in this crowded field. The analytic wing continuation and total-background mixture are explicit sensitivity assumptions.

See `scientific_report.md` for conclusions, `sensitivity_models/README.md` for model use, and `README.md` for offline reproduction. Future calibration needs include uncrowded blank sky/wings, per-source raw-linearity histories, absolute photometry/astrometry and target-instrument spectral/PSF data. No0.2arcsec ULTIMATE measurement, dust truth or new ML validation is claimed.''')]
nb=n.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python (phd)','language':'python','name':'hawki-phd'},'language_info':{'name':'python','version':'3.12.15'}})
n.validate(nb);n.write(nb,O/'empirical_calibration.ipynb');print('Notebook scaffold written')
