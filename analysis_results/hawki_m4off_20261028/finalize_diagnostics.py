"""Additional diagnostics; reads completed measurements, never refits science or ML."""
from pathlib import Path
import json, os
os.environ.setdefault('MPLCONFIGDIR','/tmp/hawki_m4_mpl')
import numpy as np,pandas as pd
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
s=pd.read_csv(O/'science_star_table.csv');s=s[s.primary_star]
fig,axs=plt.subplots(2,5,figsize=(19,7),layout='constrained')
for row,col,label in [(0,'q','Axis ratio q'),(1,'beta','Moffat beta (fit dependent)')]:
 lo,hi=s[col].quantile([.05,.95])
 for ax,(field,g) in zip(axs[row],s.groupby('field')):
  im=ax.scatter(g.x,g.y,c=g[col],s=13,vmin=lo,vmax=hi);ax.set(title=field,xlabel='x (stack pixels)',ylabel='y (stack pixels)');fig.colorbar(im,ax=ax,label=label,shrink=.7)
for ext in ['png','pdf']:fig.savefig(O/'figures'/('spatial_shape_and_wings.'+ext),dpi=170)
plt.close(fig)
# Same estimator and masks, different fields; not matched observing depths.
co=pd.read_csv(O/'background_covariance.csv');ap=pd.read_csv(O/'aperture_noise.csv');nc=pd.read_csv(O/'ngc_noise_covariance.csv');na=pd.read_csv(O/'ngc_noise_apertures.csv')
fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained');rows=[]
for label,c,a in [('M4 tile',co[(co.field=='tile0')&(co.kind=='grid')],ap[(ap.field=='tile0')&(ap.kind=='grid')]),('NGC3256 same estimator',nc,na)]:
 c=c[(c.mesh==128)&(c.dilation_pixels==12)];a=a[(a.mesh==128)&(a.dilation_pixels==12)&(a.status=='ok')]
 t=c[c.dy==0].groupby('dx').correlation.median();axs[0].plot(t.index,t,'o-',label=label)
 t=a[a.radius_pixels<=16].groupby('radius_pixels').ratio_pixel_MAD.median();axs[1].plot(t.index,t,'o-',label=label)
 row=dict(field=label,rho_x1=c[(c.dx==1)&(c.dy==0)].correlation.median(),rho_y1=c[(c.dx==0)&(c.dy==1)].correlation.median())
 row.update({'excess_R'+str(int(k)):v for k,v in t.items()});rows.append(row)
axs[0].set(xlabel='Pixel lag in x',ylabel='Masked correlation');axs[1].set(xlabel='Circular aperture radius (pixels)',ylabel='MAD noise / pixel MAD sqrt(N)')
for ax in axs:ax.legend(fontsize=9)
for ext in ['png','pdf']:fig.savefig(O/'figures'/('NGC3256_same_operator_noise.'+ext),dpi=170)
plt.close(fig);pd.DataFrame(rows).to_csv(O/'same_operator_noise_summary.csv',index=False)
# Match spatial cells, not incompatible source_local_id values, across bright/faint selections.
b=pd.read_csv(O/'broad_peak_selection/psf_fits.csv');b=b[b.accepted]
f=pd.read_csv(O/'psf_fits.csv');f=f[f.accepted]
keys=['field','bx','by'];cols=['fwhm_arcsec','q','beta'];bc=b.groupby(keys)[cols].median();fc=f.groupby(keys)[cols].median();d=fc.join(bc,lsuffix='_faint',rsuffix='_broad',how='inner')
for col in cols:d['delta_'+col]=d[col+'_faint']-d[col+'_broad']
d.to_csv(O/'brightness_selection_matched_cells.csv');summary=d.groupby('field')[[('delta_'+c) for c in cols]].median();summary.to_csv(O/'brightness_selection_sensitivity.csv')
w=pd.read_csv(O/'fit_window_sensitivity.csv');w=w[w.accepted];a=w[w.radius_pixels==13].merge(w[w.radius_pixels==20],on=['field','source_local_id'],suffixes=('_13','_20'))
for col in cols:a['delta_'+col]=a[col+'_13']-a[col+'_20']
a.to_csv(O/'fit_window_paired.csv',index=False);a.groupby('field')[['delta_'+c for c in cols]].median().to_csv(O/'fit_window_summary.csv')
# Explicitly label the fallback detector kernels and measured-wing support.
p=O/'sensitivity_models/PSF_kernel_manifest.json';manifest=json.loads(p.read_text());sm=pd.read_csv(O/'PSF_summary.csv').set_index('field')
for r in manifest:
 n=int(sm.loc[r['field'],'n_wing_reliable']);r.update(n_strict_wing_stars=n,wing_selection='strict wing sample' if n>=5 else 'fallback primary core sample; wings insufficiently validated',calibration_scope='measured core / analytic wing extrapolation; finite grid normalization',orientation_frame='original science-image pixel axes; use sky_PA_deg in joint samples for sky-frame rotations')
p.write_text(json.dumps(manifest,indent=2))
print(pd.DataFrame(rows).to_string(index=False));print('Bright/faint cell sensitivity\n',summary.to_string());print('Window13 minus20\n',a.groupby('field')[['delta_'+c for c in cols]].median().to_string())
