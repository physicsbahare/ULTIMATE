"""Build and execute the preliminary ML notebook using the existing phd kernel."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

OUT=Path(__file__).resolve().parent


def run():
    nb=nbformat.v4.new_notebook()
    md,code=nbformat.v4.new_markdown_cell,nbformat.v4.new_code_cell
    nb.cells=[
        md('# ULTIMATE: effective-attenuation statistics and morphology correction\n\n'
           '## tl;dr\n\nExecuted exploratory grouped ML using the previously explored26 galaxies; '
           'four source-product controls are excluded from fitting. Extra NIR features help '
           'several operational targets, while a robust primary GLAO ML gain is not established. '
           'The untouched120-galaxy final-evaluation sample is not used here.'),
        code("from pathlib import Path\nimport sys, json, io, contextlib\nimport pandas as pd\n"
             "from IPython.display import display, Markdown, Image\n"
             "O=Path.cwd()\nif not (O/'ml_data.py').exists(): O=O/'analysis_results/ml_feasibility_20261027'\n"
             "sys.path.insert(0,str(O.resolve()))\nimport ml_data, ml_benchmark, ml_postprocess, label_quality_audit, write_ml_report\n"
             "pd.set_option('display.max_columns',12)"),
        md('## Context & Methods\n\n### Key assumptions\n\n'
           'Labels are operational dusty/clear DR1 contrasts with unresolved physical '
           'systematics. X contains dusty observable properties only. Each galaxy keeps '
           'all orientations/noise draws in one role. Known centers/distances and R<12kpc '
           'are idealizations. Actual LSSTg/2MASSJ/Ks retain their identities. The z=0.1 '
           'distance experiment is fixed-rest-band, not exact observer-frame ULTIMATE photometry.'),
        code("display(Markdown((O/'PROTOCOL.md').read_text()))"),
        md('### Execute or resume\n\n'
           'This reruns label construction, resumes completed observable extraction and '
           'grouped fits, and recomputes aggregation, diagnostic figures and reports. '
           'No new-galaxy scientific images are opened. Prediction checkpoints avoid '
           'repeating the completed primary fits. The post-protocol empirical sensitivity '
           'has a separate explicit reproduction entry point.'),
        code("with contextlib.redirect_stdout(io.StringIO()) as progress:\n"
             "    features, labels = ml_data.build()\n    ml_benchmark.run()\n"
             "    ml_postprocess.run()\n    label_quality_audit.run()\n    write_ml_report.run()\n"
             "print('Executed/resumed primary grouped benchmark and recomputed summaries.')\n"
             "print('Feature rows:',len(features),'label rows:',len(labels))\n"
             "print('Eligible independent galaxies:',labels.loc[~labels.zero_projected_dust,'subhalo_id'].nunique())"),
        md('## Data\n\nThe original26 objects are development-only. Source-null controls '
           'are excluded from fitting; zero SFR is not a dust-free criterion. '
           'Partition metadata are shown without opening new final-evaluation images.'),
        code("display(pd.read_csv(O/'expansion/galaxy_partitions.csv').groupby('partition').agg(n_galaxies=('subhalo_id','nunique')))\n"
             "display(labels.groupby('subhalo_id').first()[['zero_projected_dust','aperture_limited']])\n"
             "display(pd.read_csv(O/'preliminary_cv_splits.csv').groupby(['fold','role']).size().unstack())\n"
             "display(json.loads((O/'feature_provenance.json').read_text()))"),
        md('## Results\n\n### Held-out baselines and the role of extra bands\n\n'
           'All errors average draws and views within each galaxy before averaging '
           'the22 galaxies. Bootstrap intervals exclude physical source uncertainty '
           'and do not fully resample overlapping model-training sets.'),
        code("summary=pd.read_csv(O/'heldout_summary.csv')\n"
             "display(summary[(summary.condition=='original_noise') & (summary['mode']=='glao') & (summary.bandset=='g_J_Ks')][['model','target','MAE','MAE_CI_low','MAE_CI_high']])\n"
             "display(Image(filename=str(O/'figures/01_grouped_ML_errors.png')))\n"
             "display(Image(filename=str(O/'figures/03_extra_bands_vs_resolution.png')))"),
        md('### Seeing versus GLAO, with noise ablations\n\n'
           'Positive paired error reduction favors GLAO. Primary ridge/forest '
           'intervals include zero across targets. Noiseless and equal-noise '
           'conditions separate spatial transfer from added-noise assumptions.'),
        code("display(Image(filename=str(O/'figures/02_GLAO_ML_ablation.png')))\n"
             "display(Image(filename=str(O/'figures/04_heldout_predictions.png')))") ,
        md('### Uncertainty, shifted tests and correction\n\n'
           'Five calibration galaxies per fold provide coarse nominal80% '
           'simultaneous intervals. Empirical undercoverage and source-null failures '
           'remain visible. Correction is scored against native clear morphology '
           'and leaves PSF/noise error; constant corrections also help.'),
        code("display(Image(filename=str(O/'figures/05_uncertainty_and_OOD.png')))\n"
             "display(Image(filename=str(O/'figures/06_morphology_correction.png')))\n"
             "display(pd.read_csv(O/'source_null_label_audit.csv'))\n"
             "display(pd.read_csv(O/'label_policy_uncertainty_summary.csv'))"),
        md('### HAWK-I empirical constraints and conditional sensitivity\n\n'
           'Processed official reduced science/variance/confidence cutouts. '
           'Real HAWK-I widths are not ULTIMATE resolution. The post-protocol '
           'wing/local-covariance stress is saved separately and does not reproduce '
           'all real larger-scale sky noise.'),
        code("display(Image(filename=str(O/'hawki/reduced_fit_inspection.png')))\n"
             "display(Image(filename=str(O/'hawki/reduced_noise.png')))\n"
             "display(pd.read_csv(O/'empirical_stress_summary.csv'))\n"
             "display(json.loads((O/'empirical_stress_assumptions.json').read_text()))"),
        md('### Information-boundary tests\n\nTest-truth perturbation must not change '
           'predictions/intervals. The120-galaxy final set remains absent from this CV.'),
        code("import unittest, test_ml_integrity\n"
             "result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(test_ml_integrity))\n"
             "assert result.wasSuccessful()\nprint('Integrity tests passed:',result.testsRun)"),
        md('## Takeaways\n\nThe report separates prediction of operational simulation '
           'labels, physical attribution, conditional instrument comparisons and '
           'future final-sample evaluation.'),
        code("display(Markdown((O/'scientific_report.md').read_text()))"),
    ]
    nb.metadata['kernelspec']={'display_name':'Python (phd)','language':'python','name':'phd'}
    NotebookClient(nb,timeout=900,kernel_name='phd',resources={'metadata':{'path':str(OUT)}}).execute()
    nbformat.validate(nb)
    assert not any(o.output_type=='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs)
    nbformat.write(nb,OUT/'ULTIMATE_preliminary_ML.ipynb')
    html,_=HTMLExporter().from_notebook_node(nb)
    (OUT/'ULTIMATE_preliminary_ML.html').write_text(html)
    print('Executed notebook and exported HTML:',OUT/'ULTIMATE_preliminary_ML.ipynb')


if __name__=='__main__':run()
