from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from astropy.io import fits
from scipy.signal import fftconvolve,convolve2d
from forward_physics import cosmology,photon_rate_jy,ARCSEC_PER_RAD
from imaging import gaussian_kernel
from instrument import setup_instrument
O=Path(__file__).resolve().parent; S=O/'sources'; checks={}
# Connector text snapshots had one transport-added trailing newline; restore exact pinned blobs when proven.
manifest=[]
for prefix,treefile in [('calculator','calculator_tree.json'),('eazy','stellar_template_tree.json'),('forward_repo','forward_repository_tree.json')]:
 tree=json.loads((S/treefile).read_text()); entries={x['path']:x for x in tree['tree'] if x['type']=='blob'}
 for p in (S/prefix).rglob('*'):
  if not p.is_file(): continue
  rel=str(p.relative_to(S/prefix))
  if rel not in entries: continue
  raw=p.read_bytes(); expected=entries[rel]
  def gitsha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
  if gitsha(raw)!=expected['sha']:
   candidates=[raw[:-1],raw.rstrip(b'\r\n'),raw.rstrip(b'\r\n')+b'\n',raw[:-1].replace(b'\n',b'\r\n'),raw.rstrip(b'\r\n').replace(b'\n',b'\r\n'),raw.rstrip(b'\r\n').replace(b'\n',b'\r\n')+b'\r\n']
   matches=[v for v in candidates if gitsha(v)==expected['sha']]
   if matches: raw=matches[0];p.write_bytes(raw)
  assert gitsha(raw)==expected['sha'],str(p)
  manifest.append({'path':str(p.relative_to(O)),'upstream_commit':tree['sha'],'git_blob_sha1':expected['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
# The three explicitly requested documents also match the pinned forward-repository tree.
tree=json.loads((S/'forward_repository_tree.json').read_text()); entries={x['path']:x for x in tree['tree'] if x['type']=='blob'}
for rel in ['docs/PASSIVE_DISK_Z3_METHOD.md','docs/JWST_ARTIFICIAL_REDSHIFTING_METHOD_AND_LIMITATIONS.md','README_JWST_artificial_redshifting.md']:
 p=S/Path(rel).name; raw=p.read_bytes(); e=entries[rel]
 if gitsha(raw)!=e['sha'] and gitsha(raw[:-1])==e['sha']:raw=raw[:-1];p.write_bytes(raw)
 assert gitsha(raw)==e['sha']
 manifest.append({'path':str(p.relative_to(O)),'upstream_commit':tree['sha'],'git_blob_sha1':e['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
(S/'pinned_source_manifest.json').write_text(json.dumps(manifest,indent=2)); checks['pinned_git_blobs_validated']=len(manifest)
# Cosmological radiometry: compare source luminosity to specific intensity times angular area independently.
rows=[]
physical_area_pc2=10000.; I=1e6; pc_m=3.085677581491367e16
Lnu=4*np.pi*I*1e-26*physical_area_pc2*pc_m**2
for z in [.1,.3,.6,1.,3.]:
 da=cosmology.angular_diameter_distance(z).to_value('m'); dl=cosmology.luminosity_distance(z).to_value('m')
 flux_sb=I/(1+z)**3*physical_area_pc2*pc_m**2/da**2
 flux_L=(1+z)*Lnu/(4*np.pi*dl**2)/1e-26
 rows.append({'z':z,'relative_error':abs(flux_sb/flux_L-1)})
assert max(r['relative_error'] for r in rows)<1e-12; checks['distance_flux_duality']=rows
# Convolution+aperture noise: analytical kernel-squared variance versus independent simulations.
k=convolve2d(gaussian_kernel(2.5),np.ones((5,5)),mode='full'); rng=np.random.default_rng(323)
samples=[]
for _ in range(2000):
 noise=rng.normal(0,3,k.shape); samples.append(np.sum(k*noise))
expected=9*np.sum(k*k); checks['aperture_variance_empirical_ratio']=float(np.var(samples)/expected)
assert abs(checks['aperture_variance_empirical_ratio']-1)<.08
# Corrected point-source limiting magnitudes; do not present them as resolved surface-brightness limits.
inst=setup_instrument(); exact={r['band']:r for r in json.loads((O/'calculator_exact_components.json').read_text())}
limits=[]
for b in inst[4:]:
 for mode in ['seeing','glao']:
  for hours in [.25,1,4]:
   T=hours*3600; N=int(T/60); diam=b[mode+'_fwhm_arcsec']; npix=np.pi*(diam/.1)**2/4
   bg=npix*((b['background_e_s_pixel']+b['dark_e_s'])*T+N*b['read_noise_e']**2)
   source_half=(25+np.sqrt(25**2+4*25*bg))/2
   jy=source_half/(.5*b['flat_e_s_per_jy']*T)
   limits.append({'band':b['band'],'mode':mode,'hours':hours,'nexp':N,'read_variance_aperture_e2':npix*N*b['read_noise_e']**2,'limit_AB_5sigma_50pct_aperture':-2.5*np.log10(jy/3631),'source_rate_per_jy_relative_to_calculator':b['flat_e_s_per_jy']/(exact[b['band']]['AB15_e_s_published']/(3631*10**(-6)))-1})
pd.DataFrame(limits).to_csv(O/'corrected_point_source_sensitivity.csv',index=False)
checks['electron_conversion_max_fractional_vs_central_wavelength']=max(abs(x['source_rate_per_jy_relative_to_calculator']) for x in limits)
# All preexisting result files: new work must leave their contents unchanged. Store current audit hashes.
old=O.parent
checks['original_pilot_sha256']=hashlib.sha256((old.parent/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb').read_bytes()).hexdigest()
checks['original_pilot_matches_previous_run']=checks['original_pilot_sha256']==json.loads((old/'validation.json').read_text())['original_notebook_sha256']
assert checks['original_pilot_matches_previous_run']
checks['source_only_shape_files_prohibited_in_fitter']=not any(s in (O/'screen_inference.py').read_text() for s in ['input_cache','dusty','dustmass','nodust','fits.getdata'])
assert checks['source_only_shape_files_prohibited_in_fitter']
checks['scientific_review']='Independent reviewer found no critical physics bug; false screen rejection from population/template mismatch and unconditioned marginal SNR selection prohibit a physical geometry-detection claim.'
(O/'physics_validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
