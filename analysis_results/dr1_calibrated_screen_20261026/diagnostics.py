"""Read-only source audits and independent post-fit diagnostics."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import json,hashlib,sys,tarfile,io
import numpy as np,pandas as pd
from scipy.optimize import nnls
from astropy.io import fits
import experiment as e
O=e.O

def audit():
 inventory=json.loads((O.parent/'archive_inventory.json').read_text())
 names=[r['name'] for r in inventory];bands=sorted({n.split('_O1_')[1][:-5] for n in names if '_O1_' in n and n.endswith('.fits') and '_nodust' not in n and not any(t in n for t in ['dustmass','stellarage','stellarmass','stellarmetallicity'])})
 (O/'local_inventory.json').write_text(json.dumps(dict(local_archives=[str(p.relative_to(O.parent.parent)) for p in (O.parent.parent/'TNG50_SKIRT').rglob('*.tar*')],galaxies=sorted({n.split('_')[0] for n in names}),archive_members=len(names),O1_available_bands=bands,original_published_filter_count=18,local_bands=len(bands),analysis_bands=e.BANDS,other_galaxy_validation=False),indent=2))
 p=np.load(O/'population_training.npz');cov=p['cov'];v=p['eigenvectors'];eig=p['eigenvalues'];h=e.contrasts(7);k=h@e.kappa(e.WAVE);k/=np.linalg.norm(k)
 rows=[]
 for n in [1,2,3]:
  q,_=np.linalg.qr(h@v[:,:n]);rows.append(dict(n_population_PCs=n,training_variance_fraction=eig[:n].sum()/eig.sum(),dust_direction_squared_projection=float(np.sum((q.T@k)**2))))
 pd.DataFrame(rows).to_csv(O/'population_dust_identifiability.csv',index=False)
 clear,_=e.load();block=clear.reshape(7,40,10,40,10).mean(axis=(2,4));xy=np.arange(40)+.5-20;yy,xx=np.meshgrid(xy,xy,indexing='ij');mask=(xx>=4)&(xx<=12)&(abs(yy)<8)
 test=block[:,mask].T;rat=test/test[:,-1,None];frac=rat/p['median_ratios']-1;center=np.mean(p['fractional_colours'],axis=0)
 projection=[]
 for rank in [1,2]:
  residual=frac-(frac@v[:,:rank])@v[:,:rank].T
  projection.append(dict(rank=rank,heldout_bins=len(frac),median_absolute_fractional_colour_residual=float(np.median(abs(residual))),p95_absolute_fractional_colour_residual=float(np.quantile(abs(residual),.95))))
 pd.DataFrame(projection).to_csv(O/'heldout_population_basis.csv',index=False)
 # External library comparison is diagnostic ONLY, no new intrinsic inference templates.
 from stellar_models import load_stellar_library
 old=[]
 for prior in ['near_clear','broad']:
  wave,seds,ids=load_stellar_library(prior);t=np.array([np.interp(e.WAVE,wave,s) for s in seds]);t/=t[:,-1,None]
  distance=np.sqrt(np.mean(((rat[:,None,:]-t[None,:,:])/np.maximum(rat[:,None,:],1e-9))**2,axis=2))
  best=distance.min(axis=1);old.append(dict(prior=prior,n_templates=len(t),source_ids=ids.tolist(),median_best_fractional_rms=float(np.median(best)),p95_best_fractional_rms=float(np.quantile(best,.95))))
 (O/'old_population_template_audit.json').write_text(json.dumps(old,indent=2))
 # Band-effective coefficient sensitivity to SED and finite widths, proxy passbands.
 widths=np.array([.14,.14,.15,.10,.162,.251,.262]);rows=[]
 wave,seds,ids=load_stellar_library('broad')
 for j,(lam,width) in enumerate(zip(e.WAVE,widths)):
  w=np.linspace(lam-width/2,lam+width/2,501)
  for si,sed in enumerate(seds):
   f=np.interp(w,wave,sed);resp=f/w
   for ebv in [.05,.15,.35]:
    ratio=np.trapezoid(resp*10**(-.4*ebv*e.kappa(w)),w)/np.trapezoid(resp,w)
    keff=-2.5*np.log10(ratio)/ebv
    rows.append(dict(band=e.LABELS[j],template=si,E_BV=ebv,k_effective=keff,k_pivot=e.kappa(lam),relative_difference=keff/e.kappa(lam)-1,width_um=width))
 pd.DataFrame(rows).to_csv(O/'within_band_SED_sensitivity.csv',index=False)
 # Age and metallicity are read ONLY after fits; retain cropped maps here for audit.
 wanted={f'TNG294866_O1_{s}.fits' for s in ['stellarage','stellarmetallicity','stellarmass']};maps={};headers={}
 with tarfile.open(O.parent.parent/'TNG50_SKIRT/downloads/TNG50_DR1_294866.tar.gz','r|gz') as tar:
  for m in tar:
   if m.name in wanted:
    raw=tar.extractfile(m).read()
    with fits.open(io.BytesIO(raw)) as hd:
     maps[m.name.split('_O1_')[1][:-5]]=np.array(hd[0].data[600:1000,600:1000],dtype='f4');headers[m.name]={'unit':hd[0].header.get('BUNIT'),'sha256_archive_member':hashlib.sha256(raw).hexdigest()}
    if len(maps)==3:break
 np.savez_compressed(O/'postfit_physical_maps_O1.npz',**maps)
 (O/'postfit_map_provenance.json').write_text(json.dumps(headers,indent=2))
 rows=[]
 for name,arr in maps.items():
  bins=arr.reshape(40,10,40,10).mean(axis=(1,3));rows.append(dict(map=name,training_median=float(np.median(bins[(xx<-4)&(xx>-14)&(abs(yy)<10)])),heldout_median=float(np.median(bins[mask])),heldout_min=float(bins[mask].min()),heldout_max=float(bins[mask].max())))
 pd.DataFrame(rows).to_csv(O/'postfit_population_truth_diagnostic.csv',index=False)
 return rows

def normalize_noise_check():
 # Worst low-SNR orientation/depth, test nonlinear-normalization moments.
 rows=[]
 for view,hours in [('O1',.25),('O4',1.)]:
  clear,dust=e.load(view);cases=e.screen_cases(clear,dust);scene=cases['B_highE_n0.7'];g=e.geometry(.3,'glao','native');rate,_=e.render(scene,.3,g)
  draws,means,covs,_=e.compressed_observation(rate,g,hours,77395,n=10000)
  ix=list(range(7));y,n,h=e.prepare_data(draws,means,covs,ix)
  center=np.concatenate([(means[j]/means[j].mean())@h.T for j in ix]);actual=np.cov(y,rowvar=False);pred=n.mean(axis=0)
  bias=(y.mean(axis=0)-center)/np.sqrt(np.diag(pred));rel=np.diag(actual)/np.diag(pred)-1
  rows.append(dict(view=view,hours=hours,n=10000,max_normalized_bias_in_sigma=float(np.max(abs(bias))),median_variance_relative_error=float(np.median(rel)),max_variance_relative_error=float(np.max(abs(rel))),min_mean_flux_normalization_snr=float(min(means[j].sum()/np.sqrt(covs[j].sum()) for j in ix))))
 pd.DataFrame(rows).to_csv(O/'normalized_noise_validation.csv',index=False)
 return rows

if __name__=='__main__':print(audit());print(normalize_noise_check())
