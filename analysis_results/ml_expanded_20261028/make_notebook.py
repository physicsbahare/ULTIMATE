"""Create an executed-artifact replay plus genuine fixed-model training notebook."""
from pathlib import Path
import nbformat as nbf

O=Path(__file__).resolve().parent
def make():
    md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
    cells=[md('''# Beyond the foreground screen: expanded interpretable ML benchmark

This notebook replays the executed 120-galaxy experiment and genuinely refits one frozen model on development data. Complete grouped candidate training, saved models, learning curves and final predictions were executed by the accompanying modules. Final predictions are read from the single evaluation receipt; this notebook never opens the final set for tuning or reruns its inference.

**Scope:** operational matched DR1 product contrasts, not validated physical dust labels or unique three-dimensional geometry. Actual LSST g / 2MASS J,Ks filters; fixed-rest-band z=0.1 distance experiment, provisional noise and Gaussian PSFs. The adaptive g-feature comparison is conditional on a common observed-Ks reference aperture.'''),
    code('''from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
from IPython.display import display,Image,Markdown
O=Path.cwd()
if not (O/'expanded_models.py').exists(): O=O/'analysis_results/ml_expanded_20261028'
sys.path.insert(0,str(O.resolve()))
from freeze_guard import verify
from expanded_features import TARGETS
from expanded_models import frame,model
assert Path(sys.executable).resolve()==Path('/home/bahareh/miniforge3/envs/phd/bin/python').resolve()
print('Frozen receipt:',verify())
display(pd.Series(json.loads((O/'FINAL_EVALUATION_COMPLETED.json').read_text())))'''),
    md('''## Independent sampling and provenance
86/14/20 frozen galaxy assignments; all views and noise draws stay grouped. Exact-zero projected-dust objects are excluded from physical-task fitting/calibration/primary scoring under the predeclared policy and retained as source controls. Zero SFR is not used as the zero-dust criterion. The 94 new archives finished before this analysis; no duplicate download was launched.'''),
    code('''inventory=pd.read_csv(O/'expanded_galaxy_inventory.csv')
display(inventory.groupby(['partition','zero_projected_dust'],dropna=False).size().rename('galaxies').to_frame())
display(pd.Series(json.loads((O/'POSTFINAL_VALIDATION.json').read_text())['checks']))
display(pd.read_csv(O/'recommended_settings.csv'))'''),
    md('''## Executed training replay: frozen recommended integrated-g model
The following fit uses development labels only. Feature preprocessing and target scaling are fit inside the estimator. No final label is loaded here. Its predictions are checked against the saved trained artifact on validation, without updating any model or hyperparameter.'''),
    code('''import joblib
choice=pd.read_csv(O/'recommended_settings.csv').set_index('target').loc['A_g']
config=dict(family=choice.family,value=int(choice.value))
data=frame('seeing_NIR',partitions=['development','validation'])
fit=data[(data.partition=='development')&~data.zero_projected_dust]
validation=data[(data.partition=='validation')&~data.zero_projected_dust]
reproduced=model(config,'seeing_NIR').fit(fit,fit[TARGETS])
prediction=reproduced.predict(validation)
saved=joblib.load(O/'models'/f'adaptive_seeing_NIR_{choice.config}.joblib')
np.testing.assert_allclose(prediction,saved.predict(validation),rtol=1e-10,atol=1e-10)
j=TARGETS.index('A_g')
scores=pd.DataFrame(dict(subhalo_id=validation.subhalo_id,absolute_error=abs(prediction[:,j]-validation.A_g)))
print('Training galaxies:',fit.subhalo_id.nunique(),'validation galaxies:',validation.subhalo_id.nunique())
print('Reproduced validation Ag MAE:',scores.groupby('subhalo_id').absolute_error.mean().mean())'''),
    md('''## One frozen final evaluation
The following tables are calculated from the saved per-orientation/per-draw predictions. MAE and RMSE weight galaxies equally; intervals resample galaxies, not pixels/views/noise. They condition on the fitted models and omit uncertain source-product systematics. The final source controls are excluded below and separately reported in the package.'''),
    code('''summary=pd.read_csv(O/'recommended_performance.csv')
display(summary.query("evaluation=='final_test' and aperture=='adaptive'")[["scenario","target","n_galaxies","MAE","MAE_low","MAE_high","RMSE","bias","galaxy_coverage"]])
gains=pd.read_csv(O/'recommended_gains.csv')
display(gains.query("evaluation=='final_test' and aperture=='adaptive' and comparison=='seeing_minus_GLAO_MAE'")[["target","gain","low","high","fraction_galaxies_improved"]])'''),
    code('''for name in ['model_and_observing_strategy_comparison','prediction_vs_atlas_target','paired_GLAO_gains','learning_curves','spatial_attenuation_statistics']:
    display(Image(filename=str(O/'figures'/(name+'.png'))))'''),
    md('''## Morphology correction and systematics
Subtract predicted native dusty-minus-clear morphology from observed dusty morphology. The comparison to native clear therefore retains PSF/noise errors; it is not a general deconvolution or intrinsic-morphology estimator. Signed effective attenuation is preserved. The four historical zero-dust controls display a coherent ≈0.12-mag g contrast even in the full field; the cause remains unresolved, with possible analytic-versus-Monte-Carlo or spectral-integration operator differences. No empirical offset is subtracted.'''),
    code('''display(summary.query("evaluation=='final_test' and aperture=='adaptive' and target in ['dR50_Ks','dC_Ks']")[["scenario","target","MAE","uncorrected_MAE","corrected_MAE"]])
display(pd.read_csv(O/'old_control_operator_envelopes.csv').query("aperture=='adaptive'")[["target","median","maximum_absolute"]])
display(pd.read_csv(O/'source_control_performance.csv').query("aperture=='adaptive' and scenario=='GLAO_NIR' and family=='median'"))'''),
    md('''## Instrumental and aperture sensitivity
HAWK-I empirical widths are not ULTIMATE specifications. Fixed nominal D50 Moffat-wing, local-covariance, software-binning and radius/center experiments quantify conditional sensitivity; the full nonlocal empirical aperture-noise excess is not reproduced. O1-only stresses do not establish orientation-general benefits.'''),
    code('''display(pd.read_csv(O/'instrument_stress_predictions_summary.csv').query("target in ['A_g','dR50_Ks','dC_Ks']")[["evaluation","scenario","target","MAE"]])
display(pd.read_csv(O/'shift_and_noise_predictions_summary.csv').query("target in ['A_g','dR50_Ks','dC_Ks']")[["evaluation","scenario","family","target","MAE"]])
display(Image(filename=str(O/'figures/aperture_target_sensitivity.png')))
display(Image(filename=str(O/'figures/representative_success_and_failure_images.png')))'''),
    code('''display(Markdown((O/'workshop_summary.md').read_text()))
print('Replay complete; no final refit, tuning, or second final inference.')''')]
    cells.insert(1,md('''**Final results (16 positive-dust galaxies; four final source controls):** recommended seeing-NIR MAE is 0.0734 mag for integrated g contrast, 0.0777 kpc for Ks ΔR50 and 0.0887 for Ks ΔC, versus median baselines 0.3003, 0.1282 and 0.1521. No positive GLAO gain interval excludes zero. GLAO improves native-clear morphology transfer, but does not establish extra dust-specific prediction information. Concentration is center-sensitive; physical-label source calibration is unresolved.'''))
    for cell in cells:
        if cell.cell_type=='code' and "for name in ['model_and_observing" in cell.source:
            cell.source="from figures import run as render_figures\nrender_figures()  # Editable Matplotlib code in figures.py; saved predictions only.\n"+cell.source
    notebook=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python (phd)','language':'python','name':'phd'},'language_info':{'name':'python','version':'3.12'}})
    nbf.write(notebook,O/'expanded_ml_executed.ipynb')
    print('Notebook source created.')

if __name__=='__main__':make()
