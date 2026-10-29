"""Derived reliability checks; no image refitting or changes to old results."""
from pathlib import Path
import pandas as pd,numpy as np
from scipy.spatial import cKDTree
O=Path(__file__).resolve().parent

def crossing(r,f,target):
 r=np.r_[0.,r];f=np.r_[0.,f];hits=np.flatnonzero(f>=target)
 if target<=0 or len(hits)==0:return np.nan
 j=hits[0]
 if j==0:return 0.
 return r[j-1]+(target-f[j-1])/(f[j]-f[j-1])*(r[j]-r[j-1])

def run():
 profiles=pd.read_csv(O/'empirical_profiles.csv');s=pd.read_csv(O/'psf_fits.csv').set_index(['field','source_local_id'])
 for key,g in profiles.groupby(['field','source_local_id']):
  g=g.sort_values('radius_arcsec');r=g.radius_arcsec.to_numpy();f=g.flux_ADU.to_numpy();s.loc[key,'empirical_growth_monotonic']=bool(np.all(np.diff(f)>=0))
  for frac in [.5,.8]:
   for ref,rr,ff in [('R2',r,f),('R15',r[:-1],f[:-1])]:s.loc[key,f'empirical_R{int(frac*100)}_{ref}_arcsec']=crossing(rr,ff,frac*ff[-1])
 s.reset_index().to_csv(O/'psf_fits.csv',index=False)
 for field,g in s.reset_index().groupby('field'):g.to_csv(O/(field+'_stars.csv'),index=False)
 # Report a geometric nonoverlapping-packing lower bound, not independent-pixel/aperture N.
 samples=pd.read_csv(O/'aperture_samples.csv');ap=pd.read_csv(O/'aperture_noise.csv');counts=[]
 for key,g in samples.groupby(['field','region','kind','radius_pixels']):
  pos=g[['x','y']].to_numpy();tree=cKDTree(pos);best=0
  for seed in range(4):
   available=np.ones(len(pos),bool);n=0
   for j in np.random.default_rng(10361+seed).permutation(len(pos)):
    if available[j]:n+=1;available[tree.query_ball_point(pos[j],2*key[-1])]=False
   best=max(best,n)
  counts.append(dict(zip(['field','region','kind','radius_pixels'],key),n_nonoverlapping_lower_bound=best))
 c=pd.DataFrame(counts);ap=ap.drop(columns=['n_nonoverlapping_lower_bound'],errors='ignore').merge(c,on=['field','region','kind','radius_pixels'],how='left',validate='many_to_one');ap.loc[(ap.dilation_pixels!=12)|(ap.mesh!=128),'n_nonoverlapping_lower_bound']=np.nan;ap.to_csv(O/'aperture_noise.csv',index=False)
 print('Signed-growth EE first crossings and geometric aperture packing recorded')
if __name__=='__main__':run()
