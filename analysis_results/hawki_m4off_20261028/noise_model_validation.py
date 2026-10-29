"""Positive-semidefinite local-correlation kernels and independent realization checks."""
from pathlib import Path
import numpy as np,pandas as pd,json
from scipy import signal,ndimage as ndi
O=Path(__file__).resolve().parent;M=O/'sensitivity_models';co=pd.read_csv(O/'background_covariance.csv');rows=[];kernels={};models=[];rng=np.random.default_rng(103610)
for field,c in co[(co.kind=='grid')&(co.mesh==128)&(co.dilation_pixels==12)].groupby('field'):
 rho=[float(c[(c.dx==1)&(c.dy==0)].correlation.median()),float(c[(c.dx==0)&(c.dy==1)].correlation.median())];v=[]
 for r in rho:
  assert 0<r<1/np.sqrt(2);a=(1-np.sqrt(1-2*r*r))/(2*r);k=np.array([a,1,a]);k/=np.linalg.norm(k);v.append(k)
 k=np.outer(v[1],v[0]);kernels[field]=k;z=signal.fftconvolve(rng.normal(size=(1536,1536)),k,mode='same')[32:-32,32:-32];std=z.std();models.append(dict(field=field,rho_x=rho[0],rho_y=rho[1],kernel_L2_norm=float(np.sqrt((k*k).sum())),pixel_arcsec=.10656,scope='local covariance sensitivity only; reproduces adjacent lags, not measured long-scale/confusion excess'))
 for axis,r in [(1,rho[0]),(0,rho[1])]:
  measured=np.corrcoef((z[:,:-1] if axis==1 else z[:-1]).ravel(),(z[:,1:] if axis==1 else z[1:]).ravel())[0,1];assert abs(measured-r)<.015;rows.append(dict(field=field,statistic='rho_x' if axis==1 else 'rho_y',predicted=r,realized=measured))
 for radius in [2,4,8,16]:
  y,x=np.mgrid[-radius:radius+1,-radius:radius+1];disk=(x*x+y*y<=radius*radius);pred=np.sqrt(np.sum(signal.fftconvolve(disk,k)**2)/disk.sum());real=signal.fftconvolve(z,disk,mode='valid').std()/std/np.sqrt(disk.sum());assert abs(real-pred)/pred<.1;rows.append(dict(field=field,statistic='ap_R'+str(radius),predicted=pred,realized=real))
np.savez_compressed(M/'local_covariance_kernels.npz',**kernels);(M/'local_noise_family.json').write_text(json.dumps(models,indent=2));pd.DataFrame(rows).to_csv(M/'local_noise_simulation_checks.csv',index=False)
full=json.loads((M/'noise_family.json').read_text())
for d in full:d['calibration_status']='Approximate total-background stress only; response residuals retained, not an instrument-noise calibration';d['R32_constraint']='Not fitted; too few independent empty apertures in crowded-field patches'
(M/'noise_family.json').write_text(json.dumps(full,indent=2));print('Local PSD noise kernels reproduce correlations and aperture response in independent realizations')
