"""Training-only geometry of adding an already-local u band; no noise forecast."""
import numpy as np,pandas as pd
import physical_model as p

def run():
 cache=np.load(p.PREV.parent/'screen_test_20261026/input_cache/O1_structured_broadbands.npz');bands=list(cache['band']);rows=[]
 for add_u in [False,True]:
  use=(['LSST_u'] if add_u else [])+p.e.BANDS;wave=np.array([cache['wave_um'][bands.index(b)] for b in use]);a=cache['clear'][[bands.index(b) for b in use],200:600,200:600];n=len(use);block=a.reshape(n,40,10,40,10).mean(axis=(2,4));x=np.arange(40)+.5-20;y,xx=np.meshgrid(x,x,indexing='ij');mask=(xx<-4)&(xx>-14)&(abs(y)<10);v=block[:,mask].T;good=(v[:,-1]>.1*np.median(v[:,-1]))&(v>0).all(axis=1);v=v[good];log=np.log(v/v[:,-1,None]);_,s,pc=np.linalg.svd(log-log.mean(axis=0),full_matrices=False);h=p.e.contrasts(n);dust=h@p.e.kappa(wave);pop=h@pc[0];cos=(dust@pop)**2/(dust@dust)/(pop@pop);rows.append(dict(bands='u+griz+JHKs' if add_u else 'griz+JHKs',n_training_regions=len(v),dust_first_log_population_PC_squared_overlap=cos,metric='unweighted log-colour direction; no observational noise or exposure claim'))
 pd.DataFrame(rows).to_csv(p.O/'existing_u_band_diagnostic.csv',index=False);print(pd.DataFrame(rows).to_string(index=False));return pd.DataFrame(rows)
if __name__=='__main__':run()
