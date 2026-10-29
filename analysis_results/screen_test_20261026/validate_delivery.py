from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np,pandas as pd,nbformat
from bs4 import BeautifulSoup
O=Path(__file__).resolve().parent; R=O.parents[1]
checks={}
n=nbformat.read(O/'ULTIMATE_static_screen_test.ipynb',as_version=4);nbformat.validate(n)
codes=[c for c in n.cells if c.cell_type=='code']
assert all(c.execution_count is not None for c in codes)
assert [c.execution_count for c in codes]==list(range(1,len(codes)+1))
assert not [o for c in codes for o in c.outputs if o.output_type=='error']
assert any('RECOMPUTE_MAIN=True' in c.source for c in codes)
checks['notebook']={'executed_code_cells':len(codes),'error_outputs':0,'full_main_recomputation':True,'embedded_png':sum('image/png' in o.get('data',{}) for c in codes for o in c.outputs)}
html=BeautifulSoup((O/'ULTIMATE_static_screen_test_preview.html').read_text(),'html.parser');assert len(html.find_all('img'))>=6
checks['HTML']={'embedded_images':len(html.find_all('img')),'tables':len(html.find_all('table'))}
for test in ['test_physics.py','test_inference_controls.py']:
 res=subprocess.run([sys.executable,str(O/test)],cwd=O,capture_output=True,text=True);assert res.returncode==0,res.stderr
 checks[test]=res.stderr.strip()
x=pd.read_csv(O/'screen_model_results.csv');good=x[x.status=='fit']
assert len(x)==575 and len(good)==574 and len(x[x.status!='fit'])==1
assert not good.duplicated(['orientation','z','mode','hours','truth','rep','population_prior']).any()
assert good[['logZ_uniform','logZ_variable','log_B_variable_uniform','chi2_uniform_profile','chi2_variable_profile']].apply(np.isfinite).all().all()
assert np.all(good.chi2_variable_profile<=good.chi2_uniform_profile+1e-8)
assert set(x.orientation)=={'O1','O2','O3','O4','O5'}
assert good.max_adjacent_background_correlation.max()<.001
tr=pd.read_csv(O/'transfer_validation.csv');assert len(tr)==48 and tr.max_flux_relative_error.max()<1e-9
ro=pd.read_csv(O/'robustness_results.csv');ps=pd.read_csv(O/'psf_robustness_oracle.csv');assert len(ps)==20
checks['cases']={'main_fit_rows':len(good),'retained_insufficient_apertures':len(x)-len(good),'robustness_rows':len(ro),'native_PSF_bound_cases':len(ps),'max_flux_error':tr.max_flux_relative_error.max()}
# Reconcile summary medians independently from the raw rows.
m=pd.read_csv(O/'screen_model_summary.csv');ind=good.groupby(['orientation','z','hours','mode','truth','population_prior']).log_B_variable_uniform.median().reset_index()
j=m.merge(ind,on=['orientation','z','hours','mode','truth','population_prior']);assert np.allclose(j.logB_median,j.log_B_variable_uniform,atol=1e-12)
# Existing TNG input content hashes from the previous completed task.
old=pd.read_csv(O.parent/'tng_input_validation.csv')
for row in old.itertuples(): assert hashlib.sha256((R/row.path).read_bytes()).hexdigest()==row.sha256
checks['previous_TNG_inputs_unchanged_SHA256']=len(old)
orig=R/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb'
assert hashlib.sha256(orig.read_bytes()).hexdigest()==json.loads((O.parent/'validation.json').read_text())['original_notebook_sha256']
checks['original_pilot_notebook_unchanged']=True
for stem in ['screen_evidence_with_null_controls','model_discrepancy_robustness','synthetic_observed_images','observable_colour_and_screen_residuals','glao_oracle_upper_bound','instrument_noise_audit']:
 for ext in ['png','pdf']:assert (O/'figures'/f'{stem}.{ext}').stat().st_size>1000
for name in ['scientific_report.md','instrument_audit.md','catalogue_status.md','parameter_provenance.json','workshop_result.md']:
 assert (O/name).stat().st_size>500
checks['paired_figures']=6
checks['physical_detection_claim']='Not established: population/discrepancy sensitivity, false physical null rejections and approximate broadband/filter synthesis remain.'
checks['DR2_endpoint']='Unverified after successful authenticated metadata/catalogue inspection; no galaxy archive downloaded.'
checks['review']='Independent read-only scientific review completed; no critical physics bug, limitations retained.'
(O/'validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
