from pathlib import Path
import nbformat as n
O=Path(__file__).resolve().parent
cells=[]
def md(x):cells.append(n.v4.new_markdown_cell(x))
def code(x):cells.append(n.v4.new_code_cell(x))
md('''# ULTIMATE–Subaru: observable structures and morphology

## Summary
GO for conditional morphology/spatial-transfer science; generic red/dark structures are not unique dust detections. Dust changes g-band half-light radii by about0.65–1.31kpc across the five views in the z=0.1/1h seeing case. The positive NIR pixel-area gain does not establish robust individual-feature detection. All intervals concern fixed-scene noise only.

## Context and scope
Executed companion to the focused full-image pilot. Actual DR1 g/J/Ks; five correlated orientations of galaxy294866. This replaces the scientific objective, not the earlier negative inference findings. No claim of unique 3D geometry. See the final report below for numerical conclusions.

The image ensemble was executed through `pilot.py` and recorded in `execution.log`. This notebook reuses that completed ensemble, independently reproduces representative observed-image measurements, and regenerates the figures/report. Set the explicit switch to rerun the new ensemble; it never runs previous Bayesian grids.''')
code('''from pathlib import Path
import json, numpy as np, pandas as pd
from IPython.display import display, Image, Markdown
import pilot as p
O=Path.cwd()
RECOMPUTE_ENSEMBLE=False
print('Existing environment:', __import__('sys').executable)
print('Bands:', p.BANDS, 'analysis FWHM [kpc]:', p.SCALES)
print('Evaluation draws per scene/condition:', p.N)
if RECOMPUTE_ENSEMBLE:
    p.run()
    import secondary_analysis, boundary_sensitivity
    secondary_analysis.run(); boundary_sensitivity.run()
''')
md('''## Methods and assumptions
Fine-minus-broad colour at 0.5/1/2kpc; native Ks fractional unsharp deficit; concentration, half-light radius and noise-corrected asymmetry. g−Ks is matched to0.8arcsec; J−Ks is matched within NIR; Ks brightness retains its native PSF. Feature criteria are fixed in PROTOCOL.md: >3 propagated noise SD and >0.05mag/0.03 fractional deficit, flux S/N>10.

Truth counterparts are used for generation/scoring, never supplied to observational measurement. Iν/(1+z)^3 gives conditional matched-rest-band degradation, not exact observer-frame photometry. Provisional instrument, ideal known sky/PSF, no galaxy evolution, one galaxy only.''')
code('''display(pd.read_csv(O/'instrument_parameters.csv')[['band','seeing_fwhm_arcsec','glao_fwhm_arcsec','read_noise_e','background_e_s_pixel']])
display(pd.read_csv(O/'noise_covariance_validation.csv'))
assert json.loads((O/'numerical_validation.json').read_text())['noise_covariance_calibration_passed']
''')
md('''## Independently reproduce a saved observational measurement
The detector images and supplied variance are the only image inputs to FilterPlan. No clear image, attenuation or dust-mass map enters this measurement.''')
code('''a=np.load(O/'observations/O1_z0.1_glao_1.0h_gaussian.npz')
g=p.make_geometry(.1,'glao')
plan=p.FilterPlan(g,'J_Ks_NIR',1.)
plan.prepare(a['SKIRT_rate_variance'])
value,sigma,mask,detected=plan.measure(a['SKIRT_observed_rate'],g['roi'])
assert np.max(abs(value[mask]-a['SKIRT_J_Ks_NIR_value'][mask]))<1e-5
assert np.max(abs(sigma[mask]-a['SKIRT_J_Ks_NIR_sigma'][mask]))<1e-5
assert np.array_equal(detected,a['SKIRT_J_Ks_NIR_detected'])
print('Eligible-ROI structure and propagated noise reproduce from float32 archives; detection mask agrees exactly.')
''')
md('''## Results: retain separate scenes, orientations and noise draws
No independent-pixel error bars. Noise intervals are for a fixed source/model, not galaxy generalization. The control scenes have no varying-dust reference; their completeness is undefined.''')
code('''f=pd.read_csv(O/'feature_draws.csv')
assert len(f)==29760
assert set(f.groupby(['view','z','mode','hours','kind','scene','method','scale_kpc']).size())=={40}
s=pd.read_csv(O/'feature_summary.csv')
display(s.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scene=="SKIRT"')[['mode','method','scale_kpc','completeness','contamination','correlation']].round(4))
display(pd.read_csv(O/'dust_morphology_bias_summary.csv').query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian"')[['mode','band','C','A','R50']].round(4))
''')
md('''## Figures
Editable plotting code lives in presentation.py and regenerates all PNG/PDF pairs from the numerical products.''')
code('''import presentation
presentation.run()
for name in ['01_reference_maps','02_seeing_GLAO_images','03_feature_recoverability','04_control_contamination']:
    display(Image(filename=str(O/f'figures/{name}.png')))
''')
code('''for name in ['05_morphology_bias','06_spatial_transfer','07_depth_sensitivity','08_SB_and_PSF_sensitivity','09_success_failure_examples']:
    display(Image(filename=str(O/f'figures/{name}.png')))
''')
md('''## Scientific report and limitations''')
code("display(Markdown((O/'scientific_report.md').read_text()))")
md('''## Optional MaNGA validation
Documentation-based proposal only; no science download or contact with collaborators.''')
code("display(Markdown((O/'MaNGA_validation_note.md').read_text()))")
md('''## Provenance and preservation''')
code("import provenance\nstatus=provenance.validate()\nprint('Previous analysis artifacts unchanged:',status['previous_artifacts_unchanged'])\nprint('Numerical checks:',json.loads((O/'numerical_validation.json').read_text()))")
nb=n.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python (phd)','language':'python','name':'phd'}});n.write(nb,O/'ULTIMATE_spatial_structure_pilot.ipynb')
