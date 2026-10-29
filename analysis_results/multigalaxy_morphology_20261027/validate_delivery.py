"""Final data/model/delivery checks with explicit metric-dependent missingness."""
from pathlib import Path
import json,hashlib,platform,base64
import numpy as np,pandas as pd
import nbformat
import audit_sample
O=Path(__file__).resolve().parent

def run(notebook=True):
 audit_sample.preserve()
 inventory=pd.read_csv(O/'archive_inventory.csv');fits=pd.read_csv(O/'fits_inventory.csv');base=pd.read_csv(O/'primary_dust_bias.csv');observed=pd.read_csv(O/'observed_morphology.csv');scores=pd.read_csv(O/'measurement_accuracy_draws.csv');gain=pd.read_csv(O/'galaxy_GLAO_gains.csv')
 assert len(inventory)==26 and inventory.sha_matches.all() and inventory.complete_pairing.all() and (inventory.current_tar_members==240).all()
 assert len(fits)==6240 and fits.valid.all() and not fits.duplicated(['subhalo_id','view','product']).any()
 assert len(base)==26*5*22 and not base.duplicated(['subhalo_id','view','band']).any()
 assert np.isfinite(base[['delta_R50','delta_C','delta_A','delta_q','attenuation_mag']]).all().all()
 bad=observed[~np.isfinite(observed[['R50','C','A','q']]).all(axis=1)];bad.to_csv(O/'noisy_morphology_failures.csv',index=False)
 assert bad.phase.eq('noise').all(),'noiseless morphology failure'
 # All finite paired scores share identical mode validity, including missing q.
 keys=['subhalo_id','view','band','z','hours','kind','draw','pairing','metric']
 for target in ['preservation_abs_error','dust_delta_abs_error']:
  check=scores.groupby(keys)[target].apply(lambda x: x.notna().sum());assert check.isin([0,2]).all()
 gcontrol=gain[gain.band=='LSST_g'].gain.dropna();assert np.max(abs(gcontrol))<1e-12
 tr=pd.read_csv(O/'transfer_validation.csv');assert tr.padded_flux_loss.max()<1e-6
 # Original archived FITS members are reconciled with the original retained manifest.
 prior=json.loads((O.parent/'screen_test_20261026/sources/skirt_stream_manifest.json').read_text());old={Path(x['archive_member']).name:x['sha256'] for x in prior};original=fits[fits.subhalo_id==294866]
 n=0
 for row in original.itertuples():
  name=Path(row.member).name
  if name in old:assert row.member_sha256==old[name];n+=1
 assert n==135
 priorpairs=pd.read_csv(O.parent/'spatial_structure_pilot_20261026/dust_morphology_paired_draws.csv')
 priorpairs=priorpairs[(priorpairs.z==.1)&(priorpairs.hours==1)&(priorpairs.kind=='gaussian')&(priorpairs.draw==-1)]
 ref=observed[(observed.subhalo_id==294866)&(observed.phase=='reference')].copy()
 ref['band']=ref.band.map({'LSST_g':'g','2MASS_Ks':'Ks','2MASS_J':'J'})
 max_view_error=0.
 for row in priorpairs.itertuples():
  sub=ref[(ref.view==row.view)&(ref['mode']==row.mode)&(ref.band==row.band)].set_index('scene')
  for k,oldk in [('R50','R50'),('C','C'),('A','A'),('q','axis_ratio')]:
   err=abs(sub.loc['dusty',k]-sub.loc['clear',k]-getattr(row,oldk));max_view_error=max(max_view_error,float(err))
 assert max_view_error<1e-10

 gs=pd.read_csv(O/'galaxy_observing_accuracy.csv');gs[~gs.preservation_abs_error_eligible|~gs.dust_delta_abs_error_eligible].to_csv(O/'noisy_metric_galaxy_exclusions.csv',index=False)
 validation=dict(galaxies=26,orientations_per_galaxy=5,paired_bands=22,FITS_members=len(fits),primary_pairs=len(base),intrinsic_rows=len(pd.read_csv(O/'intrinsic_morphology.csv')),observed_rows=len(observed),noisy_morphology_invalid_rows=len(bad),invalid_by_band=bad.groupby('band').size().to_dict(),g_identical_strategy_max_gain=float(abs(gcontrol).max()),gaussian_max_flux_loss=float(tr.padded_flux_loss.max()),old_FITS_hashes_matched=n,all_five_view_pilot_max_error=max_view_error,previous_results_files_unchanged=len(json.loads((O/'previous_results_sha256.json').read_text())),PNG_figures=len(list((O/'figures').glob('*.png'))),PDF_figures=len(list((O/'figures').glob('*.pdf'))),development_gate_passed=json.loads((O/'development_gate.json').read_text())['passed'],physical_scope='Conditional paired DR1 morphology; no final ULTIMATE forecast or unique dust attribution',q_noise_policy='Joint finite strategy draws, >=6/8 in every view; eligibility/exclusions retained',visual_inspection='Pending manual inspection of saved figures',source_physical_null='UNRESOLVED: zero projected-dust objects have nonzero image-pair residuals; no correction applied',python=platform.python_version())
 assert validation['PNG_figures']==validation['PDF_figures']==11
 if notebook:
  nb=nbformat.read(O/'ULTIMATE_multigalaxy_morphology.ipynb',as_version=4);codes=[c for c in nb.cells if c.cell_type=='code'];assert all(c.execution_count is not None for c in codes);assert not any(o.output_type=='error' for c in codes for o in c.outputs)
  validation['executed_notebook_code_cells']=len(codes);validation['embedded_notebook_images']=sum('image/png' in o.get('data',{}) for c in codes for o in c.outputs);assert validation['embedded_notebook_images']>=10
  validation['HTML_preview_exists']=(O/'ULTIMATE_multigalaxy_morphology.html').exists()
  embedded={hashlib.sha256(base64.b64decode(o['data']['image/png'])).hexdigest() for c in codes for o in c.outputs if 'image/png' in o.get('data',{})}
  expected={hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'figures').glob('*.png')}
  assert expected<=embedded,'Notebook figures differ from saved PNGs'
  validation['notebook_images_match_saved_PNGs']=True
  assert '2MASS Ks only' in (O/'scientific_report.md').read_text()
  assert (O/'scientific_report.md').read_text() in '\n'.join(o.get('data',{}).get('text/markdown','') for c in codes for o in c.outputs),'Notebook report differs from saved report'
  validation['notebook_report_matches_saved_report']=True
 if (O/'visual_inspection.json').exists():validation['visual_inspection']=json.loads((O/'visual_inspection.json').read_text())
 (O/'validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation,indent=2));return validation
if __name__=='__main__':run('--no-notebook' not in __import__('sys').argv)
