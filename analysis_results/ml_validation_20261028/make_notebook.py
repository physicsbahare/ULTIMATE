from pathlib import Path
import json,os,sys
import nbformat as n
from nbclient import NotebookClient
O=Path(__file__).resolve().parent
root=Path('/tmp/ultimate-jupyter');k=root/'kernels'/'ultimate-phd';k.mkdir(parents=True,exist_ok=True)
(k/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'phd (existing environment)','language':'python'}));os.environ['JUPYTER_PATH']=str(root)
b=n.v4.new_notebook();b.metadata.kernelspec={'display_name':'phd (existing environment)','language':'python','name':'ultimate-phd'}
b.cells=[n.v4.new_markdown_cell('''# ULTIMATE–Subaru expanded ML validation

Executed training and evaluation companion. Final20 status and results are recorded in the final-evaluation section when available. Results concern signed DR1 paired-image differences; source-control residuals prevent equating numerical prediction accuracy with calibrated physical dust recovery.

The full benchmark is implemented in `model_study.py`; exact input hashes and tuning choices are saved. This notebook independently refits representative photometric and spatial ridge models using those development-only choices and checks held-out predictions against the benchmark.'''),
n.v4.new_code_cell('''from pathlib import Path
import sys,json
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display,Image
O=Path.cwd()
assert '/phd/' in sys.executable
sys.path.insert(0,str(O))
from model_study import estimator,feature_cols,TARGETS
f=pd.read_csv(O/'feature_table.csv.gz'); y=pd.read_csv(O/'target_table.csv')
settings=json.loads((O/'model_settings.json').read_text())
pred=pd.read_csv(O/'heldout_predictions.csv.gz')
print('Independent galaxies:',f.groupby('partition').subhalo_id.nunique().to_dict())
assert not f.partition.eq('final_test').any() and not y.partition.eq('final_test').any()
'''),n.v4.new_markdown_cell('''## Methods and physical definitions

Five views and four noise draws remain with their parent galaxy. Fitting and five-fold hyperparameter selection use nonzero-projected-dust development galaxies only; validation14 never selects settings. Native targets use a common fixed12-kpc or observed-Ks adaptive aperture for both scenes. C=5 log10(R80/R20); Δ denotes dusty minus clear. Integrated attenuation is −2.5 log10(F_dusty/F_clear). Spatial median/IQR use the 1-kpc-FWHM-smoothed signed attenuation field.

Known centers/distances, deep noiseless Ks aperture selection, Gaussian moment noise and matched rest-band radiometry are idealizations. Optical-only comparisons are cleanest for fixed12; adaptive selection itself uses NIR. These are not observer-frame ULTIMATE predictions.'''),
n.v4.new_code_cell('''checks=[]
for target,kind in [('A_g','photo'),('dR50_Ks','spatial'),('dC_Ks','spatial')]:
    tag=f'fixed12_nir_seeing_{target}_ridge_{kind}_'
    cfg=settings[tag]
    data=f[(f.aperture=='fixed12')&(f.condition=='nominal')&(f['mode']=='seeing')].merge(y[y.aperture=='fixed12'],on=['subhalo_id','view','partition','aperture'],validate='many_to_one')
    train=data[(data.partition=='development')&(~data.zero_projected_dust)]
    validation=data[data.partition=='validation']
    assert set(train.subhalo_id).isdisjoint(set(validation.subhalo_id))
    model=estimator('ridge',cfg['setting']).fit(train[cfg['features']],train[target])
    prediction=model.predict(validation[cfg['features']])
    reference=pred[(pred.tag==tag)&(pred.stage=='validation')][['subhalo_id','view','draw','prediction']]
    check=validation[['subhalo_id','view','draw']].assign(refit=prediction).merge(reference,on=['subhalo_id','view','draw'],validate='one_to_one')
    np.testing.assert_allclose(check.refit,check.prediction,rtol=1e-10,atol=1e-10)
    mae=validation.assign(error=abs(validation[target]-prediction)).groupby('subhalo_id').error.mean().mean()
    checks.append(dict(target=target,kind=kind,development_galaxies=train.subhalo_id.nunique(),validation_galaxies=validation.subhalo_id.nunique(),MAE=mae,refit_max_difference=float(abs(check.refit-check.prediction).max())))
display(pd.DataFrame(checks).round(6))'''),
n.v4.new_markdown_cell('## Held-out point predictions and baselines'),n.v4.new_code_cell("display(Image(filename=str(O/'figures/model_comparison.png')))") ,
n.v4.new_code_cell("display(Image(filename=str(O/'figures/predictions_residuals.png')))") ,
n.v4.new_markdown_cell('## NIR bands and resolution\nPositive seeing-minus-GLAO MAE denotes an improvement. Intervals resample galaxies, conditional on fitted methods and the selected sample; no multiplicity correction or population-wide guarantee.'),
n.v4.new_code_cell("display(Image(filename=str(O/'figures/GLAO_increment.png')))"),
n.v4.new_markdown_cell('## Learning, uncertainty and OOD\nLearning-curve points use development group CV with tuning inside each training subset. Error bars show fold scatter, not independent-galaxy confidence intervals. Interval calibration uses seven validation galaxies and assessment uses the other seven, with each score the maximum residual over all views/draws.'),
n.v4.new_code_cell("display(Image(filename=str(O/'figures/learning_curves.png')))\ncal=pd.read_csv(O/'uncertainty_calibration.csv')\ndisplay(cal[cal.tag.isin(['fixed12_nir_seeing_A_g_ridge_photo_','fixed12_nir_seeing_dR50_Ks_ridge_spatial_','fixed12_nir_seeing_dC_Ks_ridge_spatial_'])].round(5))\nood=pd.read_csv(O/'OOD_summary.csv');display(ood[ood.tag.str.contains('seeing')].round(5))"),
n.v4.new_markdown_cell('## Aperture and source-systematic limits'),n.v4.new_code_cell("display(pd.read_csv(O/'aperture_target_sensitivity.csv').round(5))\ndisplay(pd.read_csv(O/'source_control_envelopes.csv').drop(columns='interpretation').round(5))"),
n.v4.new_markdown_cell('## HAWK-I-informed stress\nO1/two-draw stress only; empirical HAWK-I PSF shapes and correlated-noise stresses are separate from nominal ULTIMATE. HAWK-I supplies no dust truth. The long-scale covariance component is an explicit sensitivity choice, not a calibrated ESO or ULTIMATE noise model.'),
n.v4.new_code_cell("display(pd.read_csv(O/'sensitivity_noise_response.csv').round(4))\ns=pd.read_csv(O/'sensitivity_summary.csv');display(s[(s.stage=='validation')&(s.tag=='fixed12_nir_seeing_A_g_ridge_photo_')][['scenario','MAE','RMSE','bias','n_galaxies']].round(5))"),
n.v4.new_markdown_cell('''## Takeaways

Read `scientific_report.md` for the quantitative conclusions, negative results and publication assessment. The notebook refit check verifies reproducibility of selected models; it does not validate source-product physical truth, simulation-to-real transfer or a unique three-dimensional geometry. The final20 set remains sealed pending an immutable evaluation protocol and explicit resolution of the physical versus operational claim.''')]
if (O/'final_metrics.csv').exists():
 b.cells += [n.v4.new_markdown_cell('## One frozen final20 evaluation\nMethods, target definitions, model settings, artifacts and calibration widths were hashed before these galaxies were opened. No final refitting/tuning. All recorded model families are retained.'),n.v4.new_code_cell("final=pd.read_csv(O/'final_metrics.csv');lookup=pd.read_csv(O/'model_comparison.csv')[['tag','aperture','bands','mode','target','model']].drop_duplicates('tag');final=final.drop(columns='target').merge(lookup,on='tag');display(final[(final.aperture=='fixed12')&(final.bands=='nir')&(final['mode']=='seeing')].pivot(index='target',columns='model',values='MAE').round(5));display(Image(filename=str(O/'figures/final_predictions_residuals.png')))")]
 for cell in b.cells:
  if cell.cell_type=='markdown':cell.source=cell.source.replace('The final20 set remains sealed pending an immutable evaluation protocol and explicit resolution of the physical versus operational claim.','The final20 evaluation uses an immutable operational-label protocol; physical source calibration remains unresolved.')
if (O.parent/'ml_expanded_20261028/FINAL_EVALUATION_COMPLETED.json').exists():
 for cell in b.cells:
  if cell.cell_type=='markdown':cell.source=cell.source.replace('The final20 set remains sealed pending an immutable evaluation protocol and explicit resolution of the physical versus operational claim.','The canonical project final20 evaluation is already complete; these supplementary models are validation-only and must not be tested on the spent final set.').replace('Final20 status and results are recorded in the final-evaluation section when available.','The pre-existing pipeline completed one frozen final20 evaluation; supplementary models here remain validation-only.')
 b.cells += [n.v4.new_markdown_cell('## Verified canonical final result, reused without new inference\nThe pre-existing pipeline froze its own methods before final access and completed the project’s single final evaluation. Its positive-dust primary sample has16 galaxies;4 final source controls are separate. The following saved summary belongs to that canonical model family, **not** the supplementary refits above. No supplementary final inference has been run.'),n.v4.new_code_cell("canonical=pd.read_csv(O.parent/'ml_expanded_20261028/recommended_performance.csv');display(canonical[(canonical.evaluation=='final_test')&(canonical.aperture=='adaptive')&(canonical.scenario=='GLAO_NIR')][['target','family','n_galaxies','MAE','RMSE','bias','galaxy_coverage']].round(5))")]
n.validate(b);NotebookClient(b,timeout=900,kernel_name='ultimate-phd',resources={'metadata':{'path':str(O)}}).execute();n.write(b,O/'expanded_training_evaluation.ipynb');print('Executed notebook saved')
