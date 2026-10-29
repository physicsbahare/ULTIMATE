from pathlib import Path
import numpy as np,pandas as pd
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;rng=np.random.default_rng(103620)
s=pd.read_csv(O/'science_star_table.csv');ee=pd.read_csv(O/'empirical_profiles.csv').merge(s[['field','source_local_id','bx','by','wing_reliable']],on=['field','source_local_id'],validate='many_to_one');rows=[]
for (field,rad),g in ee[ee.wing_reliable].groupby(['field','radius_arcsec']):
 blocks=[x.EE_R2.dropna().to_numpy() for _,x in g.groupby(['bx','by'])];boot=[np.median(np.concatenate([blocks[i] for i in rng.integers(len(blocks),size=len(blocks))])) for _ in range(1000)];rows.append(dict(field=field,radius_arcsec=rad,n_stars=len(g),n_cells=len(blocks),median=g.EE_R2.median(),p16=g.EE_R2.quantile(.16),p84=g.EE_R2.quantile(.84),median_CI95_lo=np.quantile(boot,.025),median_CI95_hi=np.quantile(boot,.975),scope='conditional spatial-cell bootstrap; finite R2 normalization, no sky/calibration systematic included'))
z=pd.DataFrame(rows);z.to_csv(O/'EE_uncertainty.csv',index=False)
fig,axs=plt.subplots(1,5,figsize=(18,3.7),layout='constrained')
for ax,(field,g) in zip(axs,z.groupby('field')):
 ax.plot(g.radius_arcsec,g['median']);ax.fill_between(g.radius_arcsec,g.median_CI95_lo,g.median_CI95_hi,alpha=.3);ax.set(title=field,xlabel='Radius (arcsec)',ylabel='EE relative to R2',xlim=(0,1.5),ylim=(0,1.08))
for ext in ['png','pdf']:fig.savefig(O/'figures'/('EE_spatial_bootstrap.'+ext),dpi=170)
plt.close(fig);rows=[]
a=pd.read_csv(O/'aperture_noise.csv');a=a[(a.mesh==128)&(a.dilation_pixels==12)&(a.status=='ok')]
for (field,kind,rad),g in a.groupby(['field','kind','radius_pixels']):
 v=g.ratio_pixel_MAD.dropna().to_numpy();boot=np.median(v[rng.integers(len(v),size=(2000,len(v)))],axis=1);rows.append(dict(field=field,kind=kind,radius_pixels=rad,n_regions=len(v),n_geometrically_nonoverlapping_lower_bound=int(g.n_nonoverlapping_lower_bound.sum()),median=np.median(v),p16=np.quantile(v,.16),p84=np.quantile(v,.84),median_region_boot_CI95_lo=np.quantile(boot,.025),median_region_boot_CI95_hi=np.quantile(boot,.975),calibration_accepted=rad<=16,scope='regional variation; overlapping aperture centers are not independent; R32 rejected, CI omits mask/sky/source systematics'))
pd.DataFrame(rows).to_csv(O/'aperture_noise_uncertainty.csv',index=False);print('Saved spatial EE intervals and regional aperture-noise spread/intervals')
