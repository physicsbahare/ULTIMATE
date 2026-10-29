from pathlib import Path
import nbformat as nbf
O=Path(__file__).resolve().parent
n=nbf.v4.new_notebook();n.metadata['kernelspec']={'display_name':'Python (phd)','language':'python','name':'phd'}
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
n.cells=[md('''# ULTIMATE–Subaru: calibrated DR1 dust-screen experiment
## tl;dr
Controlled non-uniform screens can be recovered under a bounded empirical population ensemble. This does **not** establish robust dust inference: fixed population stress anchors and posterior-predictive failures still matter. No general ULTIMATE/GLAO or 3D geometry claim follows. These are actual DR1 bands and **matched-rest-band degradation**, not exact observer-frame photometry.

This executed notebook reruns the numerical pipeline from existing local inputs. Earlier results are read-only. No downloads, installations, DR2 investigations or ML occur. Statistical development and final evaluation are separated explicitly in `FINAL_PROTOCOL.md`.
'''),md('''## Context & Methods
Seven actual bands: LSST griz and 2MASS J/H/Ks. Clear/dusty SKIRT scenes remain structured. Screens multiply images before PSF; n=1 power law is defined by k(B)-k(V)=1. Fits use noisy normalized linear fluxes, full covariance and a bounded empirical spatial population hierarchy. Training uses a disjoint left-hand region; evaluation is on fixed right-hand apertures. The alternative adds a phenomenological dust-colour field, not a recovered physical E map.

### Key assumptions
Static galaxy; frequency-specific dimming; FlatLambdaCDM H0=70, Om=.3; provisional instrument parameters, known sky,60s split reads. Compressed Gaussian noise is checked against exact Poisson/read projection. Final500 calibration and500 evaluation draws per scene are independent within each condition. Common random numbers pair conditions. Source-dependent noise covariance is supplied by the simulation. See the separate limitations and audit reports.
'''),code("""import os, sys
from pathlib import Path
os.environ['MPLCONFIGDIR']='/tmp/ultimate-mpl'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
sys.dont_write_bytecode=True
O=Path('/home/bahareh/ULTIMATE/analysis_results/dr1_calibrated_screen_20261026')
sys.path.insert(0,str(O))
import numpy as np, pandas as pd
import experiment, diagnostics, population_stress, final_ensemble, final_stress, publish
from IPython.display import display, Image, Markdown
print(sys.executable)
assert sys.executable.startswith('/home/bahareh/miniforge3/envs/phd/')
"""),md('''## Data and numerical validation
The tests check flux transfer, frequency dimming, exposure splitting, the contrast likelihood, calibration order statistic, observed-only normalization, signed linear projection, posterior discrepancy and independent positive population generation.'''),code("""import unittest, test_validation
suite=unittest.defaultTestLoader.loadTestsFromModule(test_validation)
result=unittest.TextTestRunner(verbosity=1).run(suite)
assert result.wasSuccessful()
"""),md('''### Development experiments
These results establish the original calibration failure and test population/law, band subset, PSF, depth, binning and correlated orientations. They are not relabelled as final validation.'''),code("""development=experiment.run()
print('Development summary rows:',len(development))
"""),code("""diagnostics.audit()
display(pd.read_csv(O/'local_inventory.json') if False else pd.read_csv(O/'population_dust_identifiability.csv'))
display(pd.DataFrame(diagnostics.normalize_noise_check()))
"""),code("""stress=population_stress.run()
print('Development stress rows:',len(stress))
"""),md('''### Final experiment: independent calibration and evaluation
The final protocol was fixed after development stress testing. Population priors are unchanged. Five global-screen nulls each have500 calibration draws with bounded training-derived colour fields. New population coefficients and noise draws evaluate nulls, smooth/patch screens and unchanged SKIRT. Only the first two empirical population PCs are generated; residual covariance is included in fitting. All six spatial fields are fixed before evaluation.'''),code("""final=final_ensemble.run()
assert set(final.n_evaluation)=={500}
print('Final summary rows:',len(final))
"""),md('''### New-noise anchor checks
Fixed population settings test whether ensemble-average calibration protects individual plausible population fields. These controls are evaluated with new noise and frozen final thresholds, without adjustment.'''),code("""anchors=final_stress.run()
print('Final anchor rows:',len(anchors))
"""),md('''## Results
Exact binomial intervals condition on the chosen ensemble and cutoff. GLAO comparison bootstraps both calibration and evaluation indices, preserving common-noise pairing. No pooling of correlated views or bands as independent galaxies.'''),code("""paths=publish.build()
display(pd.read_csv(O/'FINAL_calibrated_rates.csv').query('bandset == "joint" and truth in ["B_uniform","C_gradient","C_patchy","D_SKIRT"]')[['z','strategy','mode','truth','rate','ci_low','ci_high']].round(4))
"""),code("""import residual_diagnostics
residual_diagnostics.run()
for path in sorted((O/'figures').glob('*.png'))[:4]:
    display(Image(filename=str(path)))
"""),code("""for path in sorted((O/'figures').glob('*.png'))[4:]:
    display(Image(filename=str(path)))
display(pd.read_csv(O/'GLAO_power_comparison.csv').query('z==0.3 and bandset=="joint"').round(4))
"""),md('''## Takeaways
Read the executed source-backed report below. The scope is conditional colour-field discrimination for one galaxy. Model inadequacy and population-anchor failures preclude a robust physical geometry claim. In particular, rest Ks shifts beyond ordinary ground Ks at z=.3; nominal-band noise proxies do not make that band observable.
'''),code("""display(Markdown((O/'scientific_report.md').read_text()))
""")]
nbf.validate(n);nbf.write(n,O/'Calibrated_DR1_screen_experiment.ipynb')
