from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import nbformat
from astropy.io import fits
from scipy.stats import rankdata
R=Path('/home/bahareh/ULTIMATE'); O=R/'analysis_results'; result={}
s=pd.read_csv(O/'tng_orientation_summary.csv'); sens=pd.read_csv(O/'tng_mask_aperture_sensitivity.csv')
assert list(s.orientation)==['O1','O2','O3','O4','O5'] and len(sens)==135
assert np.isfinite(s.select_dtypes('number')).all().all()
# Independent rank-Pearson computation on the stored input maps validates Spearman implementation and mask counts.
recomputed=[]
for _,row in s.iterrows():
 ori=row.orientation; d=R/'TNG50_SKIRT/pilot_294866' if ori=='O1' else O/'extracted_294866'
 a={k:fits.getdata(d/f'TNG294866_{ori}_{v}.fits').astype(float) for k,v in {'g':'LSST_g','g0':'LSST_g_nodust','ks':'2MASS_Ks','ks0':'2MASS_Ks_nodust','dust':'dustmass'}.items()}
 b={k:v.reshape(160,10,160,10).sum((1,3))/100 for k,v in a.items()}
 y,x=np.indices((160,160)); rr=np.sqrt((x-79.5)**2+(y-79.5)**2)
 with np.errstate(divide='ignore',invalid='ignore'):
  ag=2.5*(np.log10(b['g0'])-np.log10(b['g'])); ak=2.5*(np.log10(b['ks0'])-np.log10(b['ks']))
 mask=(rr<20)&(b['dust']>0)&(b['g0']>1e-4*b['g0'].max())&(b['ks0']>1e-4*b['ks0'].max())&np.isfinite(ag)&np.isfinite(ak)
 assert mask.sum()==row.n_bins
 for band,atten in [('g',ag),('ks',ak)]:
  independent_rho=np.corrcoef(rankdata(b['dust'][mask]),rankdata(atten[mask]))[0,1]
  assert np.isclose(independent_rho,row[f'rho_{band}'],atol=1e-12)
  independent_A=2.5*(np.log10(a[band+'0'].sum())-np.log10(a[band].sum()))
  assert np.isclose(independent_A,row[f'A_{band}_full_mag'],atol=1e-12)
 recomputed.append(ori)
 with fits.open(O/'attenuation_maps'/f'{ori}_maps_500pc.fits',checksum=True) as hd:
  assert len(hd)==5 and hd['A_G'].data.shape==(320,320)
  assert all(h.verify_checksum()==1 and h.verify_datasum()==1 for h in hd)
result['independent_recomputation_pass']=recomputed
notebooks={}
for name in ['pilot_reproduced','TNG294866_five_orientations']:
 n=nbformat.read(O/f'{name}.ipynb',as_version=4); nbformat.validate(n)
 code=[c for c in n.cells if c.cell_type=='code']; assert all(c.execution_count is not None for c in code)
 assert not [out for c in code for out in c.outputs if out.output_type=='error']
 assert sum(out.output_type in ['display_data','execute_result'] for c in code for out in c.outputs)>0
 notebooks[name]={'executed_code_cells':len(code),'error_outputs':0,'embedded_png_outputs':sum('image/png' in out.get('data',{}) for c in code for out in c.outputs)}
orig=nbformat.read(R/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb',as_version=4); copy=nbformat.read(O/'pilot_reproduced.ipynb',as_version=4)
oc=[c.source for c in orig.cells if c.cell_type=='code']; nc=[c.source for c in copy.cells if c.cell_type=='code']; assert len(oc)==len(nc)
assert all(a==b for a,b in zip(oc[1:],nc[1:]))
# First cell: normalize the intentional I/O adaptation, then compare the reader/import science code.
assert oc[0].split('# Lightweight FITS loader')[1]==nc[0].split('# Lightweight FITS loader')[1]
result['notebooks']=notebooks; result['pilot_science_code_preserved']=True
h=pd.read_csv(O/'hawki_metadata.csv'); c=pd.read_csv(O/'hawki_detector_metadata.csv'); p=pd.read_csv(O/'hawki_psf_candidates.csv')
assert len(h)==22 and h.structurally_valid.all() and h.size_matches.all() and (h.raw_checksum_failures==0).all() and (h.datasum_failures==0).all()
assert len(c)==88 and (c.finite_fraction==1).all() and (c.nx==2048).all() and (c.ny==2048).all()
assert h.psf_candidate_count.sum()==len(p)==677
# Compare actual input file sizes against the inventory captured before extraction/analysis.
inventory=json.loads((O/'input_inventory.json').read_text()); assert all((R/x['path']).stat().st_size==x['bytes'] for x in inventory)
result['input_inventory_sizes_unchanged']=True
result['hawki']={'exposures':22,'image_extensions':88,'raw_hdu_checksums_pass':int(h.checksum_hdus.sum()),'datasum_failures':0,'compact_source_fits':len(p),'psf_provisional':True}
for stem in ['five_orientation_maps','five_orientation_correlations','viewing_dependence','hawki_raw_preview','hawki_psf_diagnostics','talk_g_dust_maps']:
 for ext in ['png','pdf']: assert (O/'figures'/f'{stem}.{ext}').stat().st_size>1000
for name in ['scientific_summary.md','hawki_inspection_report.md','next_experiments.md','README.md','environment_inspection.md','workshop_talk_outline.md','workshop_10min.pdf']:
 assert (O/name).stat().st_size>500
result['figures']={'paired_png_pdf':6,'main_png_visually_inspected':True,'representative_pdf_renders_visually_inspected':True}
result['scientific_limitations']=['One galaxy, five dependent views','Projected surface density is not 3D geometry','No independent-pixel inference or uncertainties','Raw HAWK-I needs calibration and catalog-confirmed final-stack PSF','No realistic-noise mocks or ML training executed; instrument budget, filter curves and target distance unset','Native simulation sampling and physical smoothing limit nearby high-resolution forecasts']
result['original_notebook_sha256']=hashlib.sha256((R/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb').read_bytes()).hexdigest()
(O/'validation.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
