"""Additional blind-fit residual maps and prior/law sensitivity figure."""
import os
os.environ.setdefault("MPLCONFIGDIR","/tmp/ultimate-mpl")
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import experiment as e,final_ensemble as f

def run():
 p=np.load(e.O/'population_training.npz');clear,dust=e.load();g=e.geometry(.3,'glao','native');base,_=e.render(dust,.3,g)
 zero=np.zeros((12,)+base.shape);noise=np.random.default_rng(510031+900019+30).normal(size=(500,7,15))
 draw,mu,cv=f.generate(base,zero,f.coefficients(500,1),g,noise);y,n,h=f.prepare(draw,cv,list(range(7)));k0,k1,kdust=e.priors(g,p['cov'],p['eigenvalues'],p['eigenvectors'],list(range(7)),h,'PC2_residual')
 models=[e.GaussianModel(n[0],k) for k in [k0,k1]];pred=[m.posterior(y[0])[0] for m in models];rows=[]
 for j,band in enumerate(e.LABELS):
  sl=slice(j*14,(j+1)*14);data=draw[0,j]/draw[0,j].mean();sd=np.sqrt(np.diag(h.T@n[0,sl,sl]@h))
  pr=[1+h.T@v[sl] for v in pred]
  for i,(x,yy) in enumerate(g['coords']):rows.append(dict(band=band,x_kpc=x,y_kpc=yy,measured_normalized_flux=data[i],uniform_prediction=pr[0][i],variable_prediction=pr[1][i],uniform_residual_sigma=(data[i]-pr[0][i])/sd[i],variable_residual_sigma=(data[i]-pr[1][i])/sd[i]))
 df=pd.DataFrame(rows);df.to_csv(e.O/'FINAL_blind_residual_example.csv',index=False)
 fig,axes=plt.subplots(2,2,figsize=(9,7),layout='constrained')
 for j,band in enumerate(['g','Ks']):
  d=df[df.band==band]
  for i,(col,title) in enumerate([('uniform_residual_sigma','Uniform model'),('variable_residual_sigma','Variable-colour model')]):
   im=axes[j,i].scatter(d.x_kpc,d.y_kpc,c=d[col],cmap='RdBu_r',vmin=-5,vmax=5,s=190,marker='s');axes[j,i].set(title=f'{title}: {band}',xlabel='x [kpc]',ylabel='y [kpc]')
 fig.colorbar(im,ax=axes,label='Observed minus posterior mean / marginal noise SD');fig.suptitle('SKIRT O1, z=.3 native GLAO: first FINAL draw\nNo intrinsic template in fit; correlated residuals, model adequacy fails',fontsize=11)
 for ext in ['png','pdf']:fig.savefig(e.O/f'figures/08_blind_fit_residuals.{ext}',dpi=220,bbox_inches='tight')
 plt.close(fig)
 d=pd.read_csv(e.O/'calibrated_rates.csv');d=d[(d.z==.3)&(d.view=='O1')&(d.strategy=='native')&(d.population=='PC2_residual')&(d.bandset=='joint')&(d.truth=='C_patchy')]
 fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for ax,kind,values,label in [(axes[0],'popscale',[.5,1.,2.],'Population prior scale'),(axes[1],'dust_slope',[.7,1.,1.3],'Dust-law slope')]:
  for mode,color in [('seeing','#3776ab'),('glao','#c65b21')]:
   sub=d[(d['mode']==mode)&(d.condition<8)]
   sub=sub[sub.dust_slope==1] if kind=='popscale' else sub[sub.popscale==1]
   sub=sub.set_index(kind).loc[values];ax.plot(values,sub.rate,'o-',color=color,label=mode)
  ax.set(xlabel=label,ylabel='Calibrated patch recovery fraction',ylim=(-.03,1.05))
 axes[0].legend();fig.suptitle('Development sensitivity: same matched scenes, separately calibrated nulls\nNot the final bounded-population ensemble power',fontsize=11)
 for ext in ['png','pdf']:fig.savefig(e.O/f'figures/09_population_prior_law_sensitivity.{ext}',dpi=220,bbox_inches='tight')
 plt.close(fig);return df
if __name__=='__main__':run()
