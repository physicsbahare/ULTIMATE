from pathlib import Path
import nbformat as nbf
O=Path(__file__).resolve().parent;md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
n=nbf.v4.new_notebook();n.metadata['kernelspec']={'name':'phd','display_name':'Python (phd)','language':'python'}
n.cells=[md('''# ULTIMATE: targeted population-failure diagnosis and positive forward model
## tl;dr
**NO-GO for a robust dust-geometry claim using the current pipeline.** The catastrophic control is reproduced and explained by a misweighted population field plus dust-colour overlap. A positive multiplicative model improves contrast fits but fails physical absolute-colour tests and challenging held-out controls. Sparse apertures also discard important spatial information; these results do **not** establish a universal impossibility of broadband imaging.

This notebook executes numerical checks, reproduces the named Gaussian failure, fits the positive model to measured fluxes and analyses the completed bounded pilot. It does not repeat the old full experiment. The pilot was executed from the supplied code; its complete logs, per-draw results, thresholds and optimizer flags are retained. Set `RECOMPUTE_PILOT=True` only to rerun that focused pilot, not the previous grid.
'''),md('''## Context & Methods
Positive luminosity × convex mixtures of independent training-region source SEDs × positive attenuation, with native band-dependent PSFs. Actual DR1 griz/JHKs retain their rest-band meaning. z=.3 is conditional matched-rest-band degradation, not exact observer-frame ULTIMATE photometry.

### Key assumptions
Training region x<-4kpc; target clear SEDs never enter fitting. Templates/priors/spatial fields were frozen before new held-out patterns. Uniform versus varying E uses the same population model. Both absolute linear fluxes and normalized contrasts are examined. Luminosity is nuisance. Posterior checks use a local Laplace approximation and do not certify global/multimodal inference. Failed physical gate prevents a large evaluation or validated GLAO power forecast.
'''),code("""import os,sys
from pathlib import Path
os.environ['MPLCONFIGDIR']='/tmp/ultimate-mpl'
os.environ['OPENBLAS_NUM_THREADS']='1'
sys.dont_write_bytecode=True
O=Path('/home/bahareh/ULTIMATE/analysis_results/multiplicative_diagnosis_20261026')
sys.path.insert(0,str(O))
import numpy as np,pandas as pd
import diagnose,physical_model,make_report,degeneracy_bound,aperture_information
from IPython.display import display,Image,Markdown
print(sys.executable)
assert '/envs/phd/' in sys.executable
"""),md('''## Data and numerical checks
The existing local DR1 products and prior instrument model are read-only dependencies. Tests cover positivity, nesting, analytic gradients, training separation, uniform and structured adjoint projection, and exact loss of uniform-E information under normalization.'''),code("""import unittest,test_physical
result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(test_physical))
assert result.wasSuccessful()
"""),md('''### Reproduce only the named catastrophic control
The following is a targeted reproduction with its original seed, not a rerun of the previous grid. Covariance/spatial changes are diagnostic ablations, not adopted priors.'''),code("""mechanism=diagnose.run()
display(mechanism[['strategy','mode','variant','noise_free_statistic','reproduced_FPR']].round(4))
"""),md('''### Execute the improved model using measured fluxes
These saved observations were generated in the development experiment. Fitting accepts only their noisy fluxes and photometric covariance; no target intrinsic SED is provided.'''),code("""model=physical_model.ForwardModel('seeing')
d=np.load(O/'development_fits.npz')
checks=[]
for normalized,kind in [(False,'absolute'),(True,'contrasts')]:
    label='problem_anchor_one_noise_'+kind
    fit=model.fit(d[label+'_observed'],d[label+'_noise_cov'],normalized=normalized)
    checks.append({'likelihood':kind,'chi2':fit['chi2'],'local_predictive_p':fit['ppp'],'optimizer_success':fit['success']})
display(pd.DataFrame(checks))
"""),md('''### Bounded held-out pilot and gate
The raw physical gate failed. No large evaluation follows. The executed pilot has19 known-family calibration draws, one absolute-colour and three contrast draws per scene. Separate new spatial PC1+PC3 and training-SED patch scenarios are retained individually. Small-sample intervals are insufficient to certify a5% false-positive rate. The diagnostic MAP statistic includes prior penalties; it is not a Bayes factor.'''),code("""RECOMPUTE_PILOT=False
if RECOMPUTE_PILOT:
    import pilot
    pilot.run()
print((O/'development_gate.json').read_text())
display(pd.read_csv(O/'heldout_pilot_rates.csv'))
"""),md('''## Results: spatial information and identifiability
The positive counterexample is ambiguous in the sparse apertures but distinguishable in the full evaluation rectangle. Known-pair classification bounds are optimistic and conditional, not nuisance-marginalized recovery rates. Full-image adequacy remains unvalidated.'''),code("""display(degeneracy_bound.run())
display(aperture_information.run())
display(pd.read_csv(O/'native_adequacy_sensitivity.csv').query('field=="fine" and bin_kpc==1.5 and variable==False')[['mode','scene','chi2','ppp','success']])
"""),code("""paths=make_report.run()
for path in paths[:3]:
    display(Image(filename=str(path)))
"""),code("""for path in paths[3:]:
    display(Image(filename=str(path)))
"""),md('''## Takeaways
NO-GO for a physical geometry claim or ML with the current pipeline. The next justified step is preserving full spatial information and independently validating the stellar SED model. This is not a demonstrated fundamental failure of all broadband imaging. Read the executed report below, including optimizer and adequacy failures.
'''),code("""display(Markdown((O/'scientific_report.md').read_text()))
""")]
nbf.validate(n);nbf.write(n,O/'ULTIMATE_targeted_positive_model.ipynb')
