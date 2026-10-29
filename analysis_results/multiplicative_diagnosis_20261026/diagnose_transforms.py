"""Audit transformations of the population mode into observed flux space."""
import numpy as np,pandas as pd,json
from scipy import linalg
from diagnose import failing_scene,e,O,PREV

def run():
 clear,dust,anchor,f,d=failing_scene();p=np.load(PREV/'population_training.npz');v=p['eigenvectors'];median=p['median_ratios'];xy=np.arange(400)*.1+.05-20;y,x=np.meshgrid(xy,xy,indexing='ij');mask=(x>=3)&(x<12)&(abs(y)<8)&(clear[-1]>.1*np.median(clear[-1][(x>=3)&(x<12)&(abs(y)<8)]))
 multiplier=np.exp(d[:,None,None]*f)-1;weighted=clear/np.maximum(clear[-1],1e-20)/median[:,None,None]*multiplier
 rows=[]
 for name,array in [('log_multiplier',d[:,None,None]*f),('fractional_multiplier',multiplier),('stellar_colour_weighted_multiplier',weighted)]:
  a=array[:,mask].T
  for rank in [2,3,6]:
   res=a-(a@v[:,:rank])@v[:,:rank].T;rows.append(dict(quantity=name,n_PC=rank,residual_relative_norm=np.linalg.norm(res)/np.linalg.norm(a),max_absolute_fractional_residual=np.max(abs(res))))
 spatial=[];h=e.contrasts(15)
 for mode in ['seeing','glao']:
  g=e.geometry(.3,mode,'native');R=h@g['response'][0];target=h@(np.tanh((g['coords'][:,0]-7)/3)*np.cos(g['coords'][:,1]/6));fit=R@np.linalg.lstsq(R,target,rcond=1e-12)[0]
  spatial.append(dict(mode=mode,spatial_rank=np.linalg.matrix_rank(R),n_contrasts=14,relative_anchor_reconstruction_residual=np.linalg.norm(target-fit)/np.linalg.norm(target)))
 pd.DataFrame(rows).to_csv(O/'population_transform_projection.csv',index=False);pd.DataFrame(spatial).to_csv(O/'spatial_span_diagnostic.csv',index=False)
 print(pd.DataFrame(rows).to_string(index=False));print(spatial)
 return rows
if __name__=='__main__':run()
