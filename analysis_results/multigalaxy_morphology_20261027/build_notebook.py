from pathlib import Path
import nbformat as nbf
O=Path(__file__).resolve().parent

def build():
 nb=nbf.v4.new_notebook();cells=[]
 def md(s):cells.append(nbf.v4.new_markdown_cell(s))
 def code(s):cells.append(nbf.v4.new_code_cell(s))
 md('# Multi-galaxy dust-induced morphology and conditional GLAO transfer\n\n## tl;dr\nExecuted analysis of 26 independent TNG50-SKIRT DR1 galaxies, five repeated views each, and 22 matched dusty/clear bands. The numerical findings below are read directly from the computed galaxy-level tables. No geometry inference or exact observer-frame forecast is claimed.')
 code("from pathlib import Path\nimport sys, json\nimport numpy as np, pandas as pd\nfrom IPython.display import display, Markdown, Image\nO=Path.cwd()\nif not (O/'PROTOCOL.md').exists(): O=O/'analysis_results/multigalaxy_morphology_20261027'\nsys.path.insert(0,str(O.resolve()))\nassert (O/'PROTOCOL.md').exists()\npd.set_option('display.max_columns',12)\nsummary=pd.read_csv(O/'galaxy_bootstrap_summary.csv')\ndisplay(summary[(summary.scope=='all_26') & summary.band.isin(['LSST_g','2MASS_Ks']) & (summary.metric=='delta_R50')][['band','n_galaxies','galaxy_median','median_CI_low','median_CI_high','n_positive','n_negative']])")
 md('## Context & Methods\n\nThe primary observable is Δdust = M(dusty) − M(clear) with matched aperture, origin and sampling. The galaxy is the independent sampling unit.\n\n### Key Assumptions\nNative rest-frame images are physical counterfactual pairs. Fixed R<12-kpc light sizes are aperture-conditioned. Five fixed viewing directions are correlated. Noisy pixels remain signed. The conditional observing model uses fixed-rest-band z=0.1 distance degradation, provisional band-specific PSFs/noise, and no K corrections or evolution. LSST g remains seeing-limited. The clear counterpart enters scoring, never a method claiming observational dust identification.')
 code("display(Markdown((O/'PROTOCOL.md').read_text()))")
 md('### Execute or resume the staged analysis\n\nThis entry point checks preserved inputs, resumes completed archive/measurement work, enforces the development gate, then recomputes galaxy statistics, figures and reports. Compact per-galaxy caches prevent repeated expensive decompression. See README for a full cache-free reproduction. No network access or installations are required.')
 code("import run_stages\nrun_stages.run()\nprint('Staged analysis completed.')")
 md('## Data\n\nInventory includes current archive hashes, matching FITS products, physical units and sample provenance. The deliberately balanced sample is not population-representative.')
 code("inventory=pd.read_csv(O/'galaxy_inventory.csv')\ndisplay(inventory[['subhalo_id','role','stellar_mass_Msun','SFR_Msun_yr','dust_mass_field_Msun','min_F12_over_F30','n_aperture_limited']])\ndisplay(pd.read_csv(O/'archive_inventory.csv')[['subhalo_id','sha_matches','current_gzip_CRC','current_tar_members','complete_pairing']].head())\ndisplay(json.loads((O/'selection_audit.json').read_text()))")
 code("display(Image(filename=str(O/'figures/01_sample_selection.png')))")
 md('## Results\n\n### Native dust-induced morphology and wavelength dependence\nPoints and intervals summarize independent galaxies, not pixels or orientations. Per-view signs and ranges are preserved in the tables.')
 code("display(Image(filename=str(O/'figures/02_wavelength_dependence.png')))\ndisplay(Image(filename=str(O/'figures/03_per_galaxy_bias.png')))")
 md('### Property and viewing-angle dependence\nThese associations are exploratory. Apparent q is a light-shape diagnostic, not physical inclination; dust masses come from physical maps rather than SFR.')
 code("display(Image(filename=str(O/'figures/04_property_dependence.png')))\ndisplay(Image(filename=str(O/'figures/08_orientation_dependence.png')))")
 md('### Morphology preservation versus recovery of dust-induced changes\nThe two rows answer distinct questions. Positive paired mean error reduction favors GLAO. Galaxy-bootstrap intervals describe selected-sample scatter; the noise model and source scene are conditional.')
 code("accuracy=pd.read_csv(O/'GLAO_bootstrap_summary.csv')\ndisplay(accuracy[(accuracy.scope=='all_26') & (accuracy.band=='2MASS_Ks') & (accuracy.pairing=='independent_clear') & accuracy.metric.isin(['R50','C','A','q'])][['metric','target','seeing_mean_error','glao_mean_error','mean_gain','CI_low','CI_high','n_improved']])\ndisplay(Image(filename=str(O/'figures/05_GLAO_morphology_accuracy.png')))\ndisplay(Image(filename=str(O/'figures/06_spatial_information.png')))")
 md('### Robustness and representative cases\nThe image examples are selected by a documented galaxy-level rule and always use O1; weak or adverse results remain visible. No individual dark/red region is identified uniquely as dust.')
 code("display(Image(filename=str(O/'figures/07_measurement_robustness.png')))\ndisplay(Image(filename=str(O/'figures/09_representative_images.png')))\ndisplay(Image(filename=str(O/'figures/10_instrument_sensitivity.png')))")
 md('### Source-product residual controls and estimator limitations\n\nZero projected dust does not guarantee a perfect numerical image-pair null. These residuals are retained without subtraction; the smallest contrasts and asymmetry gains require caution.')
 code("display(Image(filename=str(O/'figures/11_source_and_estimator_controls.png')))\ndisplay(pd.read_csv(O/'zero_projected_dust_summary.csv'))")
 md('### Numerical validation\nAnalytic morphology, original-pilot reconciliation, flux conservation, aggregate Poisson/read moments and development-gate results are inspectable. Final delivery checks also verify earlier-result preservation.')
 code("import validate_science\nvalidate_science.run()\ndisplay(pd.read_csv(O/'benchmark_reproduction.csv'))\ndisplay(pd.read_csv(O/'noise_validation.csv'))\ndisplay(json.loads((O/'development_gate.json').read_text()))")
 md('## Takeaways\n\nThe scientific report is generated from the executed tables and separates robust paired simulation findings, conditional resolution comparisons, future observable measurements and unsupported population/instrument claims.')
 code("display(Markdown((O/'scientific_report.md').read_text()))")
 nb.cells=cells;nb.metadata={'kernelspec':{'display_name':'Python (phd)','language':'python','name':'phd'},'language_info':{'name':'python','version':'3.12'}}
 nbf.write(nb,O/'ULTIMATE_multigalaxy_morphology.ipynb')
if __name__=='__main__':build()
