"""Quantify finite measurement-field effects without changing final criteria."""
import pilot as p
import numpy as np,pandas as pd

def run():
 rows=[]
 for z in [.05,.1]:
  for mode in ['seeing','glao']:
   gs=p.make_geometry(z,mode);gl=dict(gs);size=2*int(np.ceil(24/gs['scale']/gs['pixel']));start=(gl['nout']-size)//2;gl['sl']=slice(start,start+size);gl['shape']=(size,size);xy=(np.arange(size)+.5-size/2)*gl['pixel']*gl['scale'];gl['y'],gl['x']=np.meshgrid(xy,xy,indexing='ij');gl['r']=np.hypot(gl['x'],gl['y']);gl['roi']=gl['r']<12
   c,d,_=p.load('O1');small,_=p.render(d,gs);large,_=p.render(d,gl);start=(size-gs['shape'][0])//2;sl=slice(start,start+gs['shape'][0])
   for method in p.METHODS:
    for scale in p.SCALES:
     vs=p.truth_maps(small,gs,method,scale);vl=p.truth_maps(large,gl,method,scale)[sl,sl];err=vs[gs['roi']]-vl[gs['roi']];rows.append(dict(z=z,mode=mode,method=method,scale_kpc=scale,RMS_boundary_difference=np.sqrt(np.mean(err**2)),max_boundary_difference=np.max(abs(err)),boundary='32kpc versus 48kpc field; R<12kpc scoring'))
 pd.DataFrame(rows).to_csv(p.O/'boundary_sensitivity.csv',index=False);print(pd.DataFrame(rows).groupby(['method','scale_kpc']).max(numeric_only=True)[['RMS_boundary_difference','max_boundary_difference']])
if __name__=='__main__':run()
