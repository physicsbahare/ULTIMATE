"""Does the constructed degeneracy persist when retaining more pixels?"""
import numpy as np,pandas as pd
from scipy import stats
import physical_model as p
from degeneracy_bound import source

def run():
 z=np.load(p.O/'positive_degeneracy_examples.npz');q=z['base_parameters'];trial=z['lambda_0.1_parameters'];rows=[]
 for mode in ['seeing','glao']:
  m=p.ForwardModel(mode);r0,_=p.e.render(source(m,q),.3,m.g);r1,_=p.e.render(source(m,trial),.3,m.g);n=r0.shape[-1];coords=(np.arange(n)+.5-n/2)*.1*m.g['scale'];yy,xx=np.meshgrid(coords,coords,indexing='ij');region=(xx>=3)&(xx<=12)&(abs(yy)<8)
  delta=(r1-r0)*3600;var=np.array([(r+b['background_e_s_pixel']+b['dark_e_s'])*3600+60*b['read_noise_e']**2 for r,b in zip(r0,m.g['inst'])]);sn=delta*delta/var
  union=(m.g['weights']>.5).any(axis=(0,1))
  for label,mask in [('pixels_inside_original_apertures',union),('evaluation_rectangle_pixels',region),('whole_frame_pixels',np.ones_like(region,dtype=bool))]:
   d2=sn[:,mask].sum();rows.append(dict(mode=mode,data=label,n_spatial_pixels=int(mask.sum()),squared_mean_separation=float(d2),optimal_pair_power_at_FPR05=float(stats.norm.sf(stats.norm.ppf(.95)-np.sqrt(d2)))))
  np.savez_compressed(p.O/f'pixel_counterexample_{mode}.npz',x=xx,y=yy,ROI=region,standardized_mean_difference=delta/np.sqrt(var))
 sparse=pd.read_csv(p.O/'conditional_identifiability_bound.csv')
 for _,r in sparse.iterrows():rows.append(dict(mode=r['mode'],data='original_15_apertures',n_spatial_pixels=15,squared_mean_separation=r.mean_separation_squared,optimal_pair_power_at_FPR05=r.optimal_simple_hypothesis_power_at_FPR05))
 table=pd.DataFrame(rows);table.to_csv(p.O/'aperture_information_loss.csv',index=False);print(table.to_string(index=False));return table
if __name__=='__main__':run()
