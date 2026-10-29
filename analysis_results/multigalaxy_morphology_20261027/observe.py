"""Conditional rest-band imaging. Reuses validated pilot radiometry, PSFs and noise moments."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy import ndimage as ndi
from morphology import Geometry,measure
O=Path(__file__).resolve().parent
_saved_import_path=sys.path.copy()
sys.path.insert(0,str(O.parent/'spatial_structure_pilot_20261026'))
import pilot as p
sys.path[:]=_saved_import_path  # Legacy pilot mutates sys.path; never leak its renderer into this run.
METRICS=['R50','C','A','q']; BANDS=['LSST_g','2MASS_J','2MASS_Ks'];N=8

def load(sid,view):
 with np.load(O/'cache'/str(sid)/f'{view}.npz') as z:
  return np.array([z[f'clear_{b}'] for b in BANDS],dtype=float),np.array([z[f'dusty_{b}'] for b in BANDS],dtype=float),z['dust'].copy()

def geometry(g):return Geometry(g['shape'][0],g['pixel']*g['scale'],12)

def spatial(images,g,size):
 sigma=size/(g['pixel']*g['scale'])/2.354820045
 f=ndi.gaussian_filter(images,sigma,mode='constant',truncate=5)
 b=ndi.gaussian_filter(images,3*sigma,mode='constant',truncate=5)
 return 1-f/np.maximum(b,1e-30)

def condition(sid,view,z=.1,hours=1.,kind='gaussian',noise=True):
 clear,dusty,_=load(sid,view);rows=[];sp=[];validation=[];snap={}
 for mode in ['seeing','glao']:
  g=p.make_geometry(z,mode,kind);mg=geometry(g)
  refs={s:p.render(im,g,False)[0] for s,im in [('clear',clear),('dusty',dusty)]}
  rates={};vars={}
  for scene,im in [('clear',clear),('dusty',dusty)]:
   rates[scene],loss=p.render(im,g);vars[scene]=p.variance(rates[scene],hours)
   validation.append(dict(subhalo_id=sid,view=view,z=z,hours=hours,kind=kind,mode=mode,scene=scene,padded_flux_loss=loss))
   for phase,imgs in [('reference',refs[scene]),('psf',rates[scene])]:
    for j,band in enumerate(BANDS):
     vals=measure(imgs[j],mg)
     rows.append(dict(subhalo_id=sid,view=view,z=z,hours=hours,kind=kind,mode=mode,scene=scene,phase=phase,draw=-1,pairing='common',band=band,**vals,A_raw=vals['A'],SNR_aperture=float(rates[scene][j][mg.mask].sum()/np.sqrt(vars[scene][j][mg.mask].sum())),PSFD50_kpc=g['widths'][j]*g['scale'],pixel_kpc=g['pixel']*g['scale']))
  if noise:
   # Reinitialization makes mode innovations paired; independent galaxies/views have distinct seeds.
   rng=np.random.default_rng(20261027+sid*101+int(view[1:])*1000003+int(z*1000))
   for draw in range(N):
    innovation=rng.standard_normal(rates['clear'].shape);independent=rng.standard_normal(innovation.shape)
    for scene,pairing,epsilon in [('clear','common',innovation),('dusty','common',innovation),('clear','independent_clear',independent)]:
     obs=rates[scene]+np.sqrt(vars[scene])*epsilon
     for j,band in enumerate(BANDS):
      vals=measure(obs[j],mg,vars[scene][j]);raw=measure(obs[j],mg)['A']
      rows.append(dict(subhalo_id=sid,view=view,z=z,hours=hours,kind=kind,mode=mode,scene=scene,phase='noise',draw=draw,pairing=pairing,band=band,**vals,A_raw=raw))
     if draw==0 and pairing=='common':snap[f'{mode}_{scene}_observed']=obs.astype('f4')
  valid=(g['r']<8)&(refs['clear'][2]>refs['clear'][2].max()*1e-4)
  sb=refs['clear'][2];edges=np.quantile(sb[valid],[1/3,2/3]);sbgroup=np.digitize(sb,edges)
  for size in [.5,1.,2.]:
   refc=spatial(refs['clear'][2],g,size);refd=spatial(refs['dusty'][2],g,size)
   obsc=spatial(rates['clear'][2],g,size);obsd=spatial(rates['dusty'][2],g,size)
   for target,truth,observed in [('dusty_morphology',refd,obsd),('dust_imprint',refd-refc,obsd-obsc)]:
    for sbsel in ['all',0,1,2]:
     mask=valid if sbsel=='all' else valid&(sbgroup==sbsel)
     rms=np.sqrt(np.mean(truth[mask]**2));err=np.sqrt(np.mean((truth[mask]-observed[mask])**2))
     corr=np.corrcoef(truth[mask],observed[mask])[0,1] if np.std(truth[mask])>1e-12 and np.std(observed[mask])>1e-12 else np.nan
     sp.append(dict(subhalo_id=sid,view=view,z=z,kind=kind,mode=mode,scale_kpc=size,target=target,SB_stratum=sbsel,truth_RMS=rms,RMSE=err,NRMSE=err/rms if rms>1e-5 else np.nan,correlation=corr,weak_reference=bool(rms<=1e-5)))
  for scene in ['clear','dusty']:snap[f'{mode}_{scene}_expected']=rates[scene].astype('f4')
  snap['reference_clear']=refs['clear'].astype('f4');snap['reference_dusty']=refs['dusty'].astype('f4');snap['pixel_kpc']=g['pixel']*g['scale']
 return rows,sp,validation,snap

def run(ids=None,sensitivity=False):
 meta=pd.read_csv(O/'galaxy_metadata.csv');pd.DataFrame([{k:v for k,v in b.items() if k not in ['wave','throughput']} for b in p.INST]).to_csv(O/'instrument_parameters.csv',index=False)
 for sid in meta.subhalo_id:
  if ids is not None and sid not in ids:continue
  if sid not in [294866,167418,626287,535051,638950]:
   assert json.loads((O/'development_gate.json').read_text())['passed'],'development gate not passed'
  dest=O/'cache'/str(sid)
  for view in [f'O{i}' for i in range(1,6)]:
   path=dest/f'{view}_observed.csv'
   if path.exists():continue
   r,s,v,snap=condition(sid,view)
   pd.DataFrame(r).to_csv(path,index=False);pd.DataFrame(s).to_csv(dest/f'{view}_spatial.csv',index=False);pd.DataFrame(v).to_csv(dest/f'{view}_transfer.csv',index=False)
   if view=='O1':np.savez_compressed(dest/'O1_example.npz',**snap)
   print('observed',sid,view,flush=True)
 if sensitivity:
  for sid in [294866,167418,626287,535051,638950]:
   dest=O/'cache'/str(sid)
   if all((dest/f).exists() for f in ['sensitivity.csv','sensitivity_spatial.csv','sensitivity_transfer.csv']):continue
   rr=[];ss=[];vv=[]
   for z,h,k in [(.1,1.,'moffat'),(.05,1.,'gaussian'),(.1,.25,'gaussian'),(.1,4.,'gaussian')]:
    r,s,v,_=condition(sid,'O1',z,h,k);rr.extend(r);ss.extend(s);vv.extend(v)
   pd.DataFrame(rr).to_csv(dest/'sensitivity.csv',index=False);pd.DataFrame(ss).to_csv(dest/'sensitivity_spatial.csv',index=False);pd.DataFrame(vv).to_csv(dest/'sensitivity_transfer.csv',index=False)
   print('sensitivity',sid,flush=True)
 for suffix,target in [('observed','observed_morphology.csv'),('spatial','spatial_information.csv'),('transfer','transfer_validation.csv')]:
  paths=[p for sid in meta.subhalo_id for p in (O/'cache'/str(sid)).glob(f'O*_{suffix}.csv')]
  if paths:pd.concat([pd.read_csv(p) for p in paths],ignore_index=True).to_csv(O/target,index=False)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--ids',nargs='*',type=int);ap.add_argument('--sensitivity',action='store_true');a=ap.parse_args();run(a.ids,a.sensitivity)
