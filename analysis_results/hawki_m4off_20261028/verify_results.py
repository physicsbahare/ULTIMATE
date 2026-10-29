"""Read-only evidence checks plus an independent fine-quadrature synthetic fit."""
from pathlib import Path
import sys,json,hashlib,importlib.util,platform
sys.dont_write_bytecode=True
import numpy as np,pandas as pd
from astropy.io import fits
O=Path(__file__).resolve().parent;R=O.parents[1];checks={}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
for r in json.loads((O/'input_integrity.json').read_text()):
 p=R/r['path'];assert sha(p)==r['sha256']
 with fits.open(p) as h:
  h.verify('exception');assert all(x.verify_checksum()==1 and x.verify_datasum()==1 for x in h)
checks['source_FITS_hashes_and_checksums']='pass'
for r in pd.read_csv(O/'ancillary_integrity.csv').to_dict('records'):assert sha(O/r['path'])==r['sha256']
checks['ancillary_hashes']='pass'
s=pd.read_csv(O/'science_star_table.csv');assert not s.duplicated(['field','source_local_id']).any();s=s[s.primary_star]
assert s.field.nunique()==5 and s.groupby('field').size().min()>100
assert np.isfinite(s[['fwhm_arcsec','q','beta']]).all().all() and s.q.between(.4,1).all()
assert (s.raw_peak<22000).all() and not s.flat_core_flag.any()
p=pd.read_csv(O/'matched_stars_primary.csv');assert len(p)==276 and p.gaia_id.nunique()==244
assert not p.duplicated(['field_pawprint','source_local_id_pawprint']).any()
checks['stellar_tables_and_pair_identity']='pass'
ee=pd.read_csv(O/'empirical_profiles.csv');e=ee[ee.radius_arcsec==2].EE_R2.dropna();assert np.allclose(e,1)
checks['finite_aperture_EE_reference']='pass'
for fn in ['positive_Moffat_PSF_kernels.npz','finite_growth_core_halo_kernels.npz','local_covariance_kernels.npz']:
 z=np.load(O/'sensitivity_models'/fn)
 for name in z.files:
  k=z[name];assert np.isfinite(k).all() and (k>=0).all()
  if fn!='local_covariance_kernels.npz':assert np.isclose(k.sum(),1,atol=1e-6)
  else:assert np.isclose(np.sum(k*k),1,atol=1e-6)
checks['positive_finite_PSF_and_covariance_kernels']='pass'
for r in json.loads((O/'sensitivity_models/noise_family.json').read_text()):assert min(r['variance_fractions'])>=0 and np.isclose(sum(r['variance_fractions']),1)
checks['PSD_noise_variance_mixtures']='pass'
ap=pd.read_csv(O/'aperture_noise.csv');assert (ap.n_nonoverlapping_lower_bound.fillna(0)<=ap.n_centres.fillna(0)).all()
assert pd.read_csv(O/'fits_provenance.csv').wcs_roundtrip_max_pixel.max()<1e-6
checks['aperture_packing_and_WCS']='pass'
# Generate 9x9 midpoint-integrated data independently of 3x3 fit quadrature.
spec=importlib.util.spec_from_file_location('psf',O/'measure_psf.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
y,x=np.indices((41,41));true=dict(cx=20.23,cy=19.73,ax=2.7,ay=2.25,beta=3.1,theta=.4);cut=np.zeros((41,41));ct=np.cos(true['theta']);st=np.sin(true['theta'])
for oy in (np.arange(9)+.5)/9-.5:
 for ox in (np.arange(9)+.5)/9-.5:
  u=(x+ox-true['cx'])*ct+(y+oy-true['cy'])*st;v=-(x+ox-true['cx'])*st+(y+oy-true['cy'])*ct;cut+=2000*(1+(u/true['ax'])**2+(v/true['ay'])**2)**(-true['beta'])/81
cut+=.015*(x-20)-.01*(y-20)
r,_=mod.fit_star(cut,1.,.10656);fw=2*np.sqrt(2**(1/true['beta'])-1)*np.sqrt(true['ax']*true['ay'])*.10656
assert r['accepted'] and abs(r['fwhm_arcsec']/fw-1)<.01 and abs(r['dx']-.23)<.01 and abs(r['dy']+.27)<.01
checks['independent_synthetic_fit']={'truth_FWHM':fw,'recovered_FWHM':r['fwhm_arcsec'],'dx':r['dx'],'dy':r['dy'],'tolerance_FWHM_fraction':.01}
# Only frozen hashes; no final test images/labels/predictions opened.
spec=importlib.util.spec_from_file_location('guard',R/'analysis_results/ml_expanded_20261028/freeze_guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);checks['previous_ML_freeze_receipt_sha256']=guard.verify()
checks['scope']='No ML training, tuning, injection, or final-science access in this task'
checks['environment']={'python':sys.version,'executable':sys.executable,'platform':platform.platform()}
for n in ['numpy','pandas','scipy','astropy','sep','matplotlib','nbformat','nbclient']:
 m=__import__(n);checks['environment'][n]=m.__version__
(O/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
