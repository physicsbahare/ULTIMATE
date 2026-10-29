from pathlib import Path
import nbformat as nbf
R=Path('/home/bahareh/ULTIMATE'); O=R/'analysis_results'
# Preserve the original: execute a copy with only I/O locations adapted.
p=nbf.read(R/'ULTIMATE_TNG50_SKIRT_294866_dust_pilot.ipynb',as_version=4)
p.cells.insert(0,nbf.v4.new_markdown_cell('Reproduction copy: original science code retained. Only DATA_DIR and OUTPUT are adapted to actual paths. Original notebook is unchanged.'))
for c in p.cells:
 if c.cell_type=='code' and 'ROOT = Path.cwd()' in c.source:
  a=c.source.index('ROOT = Path.cwd()'); b=c.source.index('# Lightweight FITS loader')
  c.source=c.source[:a]+"ROOT = Path('/home/bahareh/ULTIMATE')\nDATA_DIR = ROOT / 'TNG50_SKIRT/pilot_294866'\nOUTPUT = ROOT / 'analysis_results/pilot_reproduction_figures'\nOUTPUT.mkdir(exist_ok=True)\n\n"+c.source[b:]
p.metadata['kernelspec']={'name':'phd','display_name':'Python 3.12 (NTHU Research)','language':'python'}
nbf.write(p,O/'pilot_reproduced.ipynb')
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(s))
def code(s): cells.append(nbf.v4.new_code_cell(s))
md('''# ULTIMATE–Subaru: five views of one TNG50-SKIRT galaxy
## tl;dr
Subhalo 294866, DR1: five orientations of **one** galaxy. The summary below is generated from executed measurements. These are ideal radiative-transfer images, not observations or a demonstration of 3D dust recovery.''')
md('''## Context & Methods
Effective attenuation is $A_\lambda=-2.5\log_{10}(I_\mathrm{dust}/I_\mathrm{nodust})$. Integrated attenuation uses the ratio of summed intensities, not mean pixel attenuation. Common pixel solid angle cancels for registered equal-area images; physical pixels are 100 pc, not angular pixels.

### Key Assumptions
Match the original pilot exactly: full-frame integrated flux; statistics from 1-kpc block means within R < 20 kpc, positive projected dust, both dust-free bands above $10^{-4}$ of their respective binned full-frame peaks, and finite attenuation in both bands. Block-average intensities **before** taking ratios. Maps use 0.5-kpc means. No PSF smoothing is implied by block averaging. Thresholds are numerical surface-brightness cuts, not measured S/N. Retain negative attenuation: scattered light and radiative-transfer noise can produce it. Individual contributions cannot be separated with these files. Do not clip negatives or treat attenuation as foreground-screen optical depth.

Pixel/bin correlations are descriptive; no independent-pixel p-values or confidence intervals. O1–O5 share the same galaxy and dust distribution. Orientation IDs lack angles in the image headers, so no inclination is assigned. Surface density is a line-of-sight integral, not 3D geometry.''')
code('''from pathlib import Path
import sys, json, hashlib, importlib
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.stats import spearmanr, rankdata
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, TwoSlopeNorm
from IPython.display import display
R = Path('/home/bahareh/ULTIMATE')
O = R/'analysis_results'
F = O/'figures'; F.mkdir(exist_ok=True)
M = O/'attenuation_maps'; M.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':11, 'axes.titlesize':12, 'figure.dpi':100,
                     'savefig.dpi':300, 'pdf.fonttype':42, 'ps.fonttype':42})
environment = {'python':sys.version,'executable':sys.executable}
for name in ['astropy','numpy','scipy','pandas','matplotlib','nbformat','nbclient']:
    environment[name]=importlib.import_module(name).__version__
(O/'environment.json').write_text(json.dumps(environment,indent=2))
print(environment)''')
md('''## Data
Only 20 required FITS members were extracted for O2–O5 (g, Ks, dust-free g/Ks, projected dust). O1 uses the existing pilot files. `extraction_manifest.json` and `archive_inventory.json` preserve archive provenance. Check dimensions, units, all coordinate cards, finite values, and nonnegative input intensities.''')
code('''suffixes={'g':'LSST_g','g0':'LSST_g_nodust','ks':'2MASS_Ks','ks0':'2MASS_Ks_nodust','dust':'dustmass'}
views={}; checks=[]
coordinate_keys=['CRPIX1','CRPIX2','CRVAL1','CRVAL2','CDELT1','CDELT2','CUNIT1','CUNIT2']
for orientation in range(1,6):
    directory = R/'TNG50_SKIRT/pilot_294866' if orientation==1 else O/'extracted_294866'
    data={}; headers={}
    for key,suffix in suffixes.items():
        path=directory/f'TNG294866_O{orientation}_{suffix}.fits'
        with fits.open(path,checksum=True) as hd:
            hd.verify('exception'); assert len(hd)==1
            data[key]=hd[0].data.astype(float); headers[key]=hd[0].header.copy()
        assert data[key].shape==(1600,1600)
        assert np.isfinite(data[key]).all() and (data[key]>=0).all()
        assert headers[key]['BUNIT']==('Msun/pc2' if key=='dust' else 'MJy/sr')
        assert all(headers[key][k]==headers['g'][k] for k in coordinate_keys)
        assert headers[key]['CDELT1']==headers[key]['CDELT2']==100
        assert headers[key]['CUNIT1']==headers[key]['CUNIT2']=='pc'
        checks.append({'orientation':f'O{orientation}','band':key,'path':str(path.relative_to(R)),
                       'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                       'zero_pixels':int((data[key]==0).sum()),'unit':headers[key]['BUNIT']})
    views[f'O{orientation}']=data
pd.DataFrame(checks).to_csv(O/'tng_input_validation.csv',index=False)
print('Verified 25 aligned, finite, nonnegative 1600×1600 images; 100 pc/pixel; full frame 160 kpc.')''')
md('''### Measurement functions
The central aperture uses pixel-centre physical coordinates referenced to CRPIX=800.5. The full-frame integrals include all finite intensity pairs, including zeros. Central-aperture and faint-mask integrals are separate diagnostics. Projected mass is $\sum\Sigma_\mathrm{dust}(100\,\mathrm{pc})^2$; it is a projection-integral check, not an independent dust mass measurement.''')
code('''def block_mean(a,b):
    ny,nx=a.shape
    return a.reshape(ny//b,b,nx//b,b).mean(axis=(1,3))
def attenuation(d,d0):
    a=np.full(d.shape,np.nan)
    good=np.isfinite(d)&np.isfinite(d0)&(d>0)&(d0>0)
    a[good]=-2.5*np.log10(d[good]/d0[good])
    return a
def radius(shape,scale):
    y,x=np.indices(shape)
    return np.hypot((x+.5-shape[1]/2)*scale,(y+.5-shape[0]/2)*scale)
def integral(d,d0,mask=None):
    ok=np.isfinite(d)&np.isfinite(d0)
    if mask is not None: ok &= mask
    return -2.5*np.log10(d[ok].sum()/d0[ok].sum())
def measure(data,b=10,threshold=1e-4,rmax=20):
    q={k:block_mean(v,b) for k,v in data.items()}
    ag=attenuation(q['g'],q['g0']); ak=attenuation(q['ks'],q['ks0'])
    rr=radius(ag.shape,b*.1)
    mask=(rr<rmax)&(q['dust']>0)&(q['g0']>threshold*q['g0'].max())&(q['ks0']>threshold*q['ks0'].max())&np.isfinite(ag)&np.isfinite(ak)
    x=np.log10(q['dust'][mask])
    result={'n_bins':int(mask.sum()),'rho_g':spearmanr(x,ag[mask]).statistic,
            'rho_ks':spearmanr(x,ak[mask]).statistic,
            'negative_fraction_g':float(np.mean(ag[mask]<0)),
            'negative_fraction_ks':float(np.mean(ak[mask]<0))}
    return result,q,ag,ak,mask,rr
results=[]; sensitivity=[]; prepared={}
for orientation,data in views.items():
    stats,q,ag,ak,mask,rr=measure(data)
    row={'orientation':orientation,**stats,'projected_dust_mass_msun':data['dust'].sum()*100**2}
    for band in ['g','ks']:
        row[f'A_{band}_full_mag']=integral(data[band],data[band+'0'])
        row[f'A_{band}_R20_mag']=integral(data[band],data[band+'0'],radius(data[band].shape,.1)<20)
        row[f'A_{band}_selected_bins_mag']=integral(q[band],q[band+'0'],mask)
    # Rank residuals after fitting a cubic function of radius: exploratory, not a causal adjustment.
    X=np.column_stack([np.ones(mask.sum()),*[rr[mask]**j for j in range(1,4)]])
    def detrend(v):
        z=rankdata(v); return z-X@np.linalg.lstsq(X,z,rcond=None)[0]
    for band,a in [('g',ag),('ks',ak)]:
        row[f'rank_residual_corr_radius_cubic_{band}']=np.corrcoef(detrend(q['dust'][mask]),detrend(a[mask]))[0,1]
    results.append(row); prepared[orientation]=(q,ag,ak,mask,rr)
    for b in [5,10,20]:
        for threshold in [1e-5,1e-4,1e-3]:
            for rmax in [10,20,30]:
                st,*_=measure(data,b,threshold,rmax)
                sensitivity.append({'orientation':orientation,'bin_kpc':b*.1,'relative_threshold':threshold,'radius_kpc':rmax,**st})
summary=pd.DataFrame(results); sensitivity=pd.DataFrame(sensitivity)
summary.to_csv(O/'tng_orientation_summary.csv',index=False)
sensitivity.to_csv(O/'tng_mask_aperture_sensitivity.csv',index=False)
assert abs(summary.iloc[0].A_g_full_mag-.3344)<5e-5
assert abs(summary.iloc[0].A_ks_full_mag-.0206)<5e-5
assert abs(summary.iloc[0].rho_g-.924)<.0005
assert abs(summary.iloc[0].rho_ks-.548)<.0005
assert summary.iloc[0].n_bins==1264
# Block sums agree with native full-frame sums; checks weighting and binning arithmetic.
for data in views.values():
    for band in ['g','ks']:
        assert np.isclose(integral(data[band],data[band+'0']),integral(block_mean(data[band],10),block_mean(data[band+'0'],10)),atol=1e-12)
display(summary[['orientation','A_g_full_mag','A_ks_full_mag','n_bins','rho_g','rho_ks']].round(6))''')
md('''## Results
### Five-view maps
Identical physical fields and colour scales across orientations. The faint mask is computed at the displayed binning, so it differs from the 1-kpc statistical mask. White means masked; negative attenuation is retained. Finite colour limits clip extrema for display only. Saved FITS retain the full values and masks.''')
code('''display_maps={}
for orientation,data in views.items():
    st,q,ag,ak,mask,rr=measure(data,b=5)
    display_maps[orientation]=(q,ag,ak,mask)
    header=fits.Header({'CDELT1':500.,'CDELT2':500.,'CRPIX1':160.5,'CRPIX2':160.5,
                        'CRVAL1':0.,'CRVAL2':0.,'CUNIT1':'pc','CUNIT2':'pc'})
    hd=[fits.PrimaryHDU()]
    for name,array,unit in [('A_G',ag,'mag'),('A_KS',ak,'mag'),('SIGMA_DUST',q['dust'],'Msun/pc2'),('VALID_R20',mask.astype(np.uint8),'1')]:
        h=header.copy(); h['BUNIT']=unit
        hd.append(fits.ImageHDU(array,header=h,name=name))
    fits.HDUList(hd).writeto(M/f'{orientation}_maps_500pc.fits',overwrite=True,checksum=True)
fig,axes=plt.subplots(3,5,figsize=(16,10),layout='constrained')
for j,(orientation,(q,ag,ak,mask)) in enumerate(display_maps.items()):
    sl=np.s_[120:200,120:200]
    arrays=[np.ma.masked_where(~mask[sl],ag[sl]),np.ma.masked_where(~mask[sl],ak[sl]),np.ma.masked_less_equal(q['dust'][sl],0)]
    for i,(arr,cmap,norm) in enumerate(zip(arrays,['RdBu_r','RdBu_r','cividis'],[TwoSlopeNorm(0,vmin=-.2,vmax=1.5),TwoSlopeNorm(0,vmin=-.15,vmax=.15),LogNorm(.002,1.)])):
        im=axes[i,j].imshow(arr,origin='lower',extent=(-20,20,-20,20),cmap=cmap,norm=norm,interpolation='nearest')
        axes[i,j].set(xlabel='x (kpc)',ylabel='y (kpc)',title=f'{orientation}' if i==0 else '')
        if j==4: fig.colorbar(im,ax=axes[i,:],shrink=.8,label=['$A_g$ (mag)','$A_{Ks}$ (mag)','$\\Sigma_\\mathrm{dust}$ ($M_\\odot$ pc$^{-2}$)'][i],extend='both')
fig.suptitle('TNG50-SKIRT DR1 | subhalo 294866 | five views of one galaxy | 0.5 kpc bins',fontsize=15)
for ext in ['png','pdf']: fig.savefig(F/f'five_orientation_maps.{ext}')
plt.show()''')
md('''### Projected dust versus attenuation
All selected 1-kpc bins are shown; no independent-sample significance is implied. Intrinsic radial structure can contribute to a rank association; exploratory radius-detrended rank correlations are in the CSV, alongside aperture, threshold, and bin-size sensitivity results.''')
code('''fig,axes=plt.subplots(2,5,figsize=(16,7),sharex=True,sharey='row',layout='constrained')
for j,(orientation,(q,ag,ak,mask,rr)) in enumerate(prepared.items()):
    x=np.log10(q['dust'][mask])
    for i,(a,band) in enumerate([(ag,'g'),(ak,'Ks')]):
        ax=axes[i,j]; y=a[mask]
        ax.scatter(x,y,s=5,alpha=.22,rasterized=True,color=['#2166ac','#b35806'][i])
        ax.axhline(0,color='gray',ls='--',lw=.7)
        ax.set(title=f'{orientation} | ρ = {spearmanr(x,y).statistic:.3f}',xlabel='$\\log_{10}(\\Sigma_\\mathrm{dust}/M_\\odot\\,pc^{-2})$')
        if j==0: ax.set_ylabel(f'$A_{{{band}}}$ (mag)')
fig.suptitle('Descriptive spatial associations | 1 kpc bins | R < 20 kpc | one simulated galaxy',fontsize=14)
for ext in ['png','pdf']: fig.savefig(F/f'five_orientation_correlations.{ext}')
plt.show()''')
md('''### Viewing dependence and sensitivity
Orientation is categorical because no angles are supplied in these FITS headers. Lines link views of the same galaxy; the sensitivity envelope is a range over analysis choices, not an uncertainty interval.''')
code('''fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained')
x=np.arange(5)
for band,label,col,marker in [('g','g','#2166ac','o'),('ks','Ks','#b35806','s')]:
    axes[0].plot(x,summary[f'A_{band}_full_mag'],marker=marker,color=col,label=label)
    axes[1].plot(x,summary[f'rho_{band}'],marker=marker,color=col,label=label)
    low=sensitivity.groupby('orientation')[f'rho_{band}'].min().reindex(summary.orientation).to_numpy()
    high=sensitivity.groupby('orientation')[f'rho_{band}'].max().reindex(summary.orientation).to_numpy()
    axes[2].fill_between(x,low,high,alpha=.16,color=col)
    axes[2].plot(x,summary[f'rho_{band}'],marker=marker,color=col,label=label)
for ax in axes:
    ax.set_xticks(x,summary.orientation); ax.set_xlabel('View of subhalo 294866'); ax.legend(); ax.grid(alpha=.2)
axes[0].set(ylabel='Integrated attenuation (mag)',title='Whole 160 kpc frame')
axes[1].set(ylabel='Spearman ρ',title='Pilot mask / 1 kpc / R < 20 kpc')
axes[2].set(ylabel='Spearman ρ',title='Mask, aperture, binning sensitivity')
fig.suptitle('Five orientations are repeated views of one galaxy',fontsize=14)
for ext in ['png','pdf']: fig.savefig(F/f'viewing_dependence.{ext}')
plt.show()
display(summary[['orientation','negative_fraction_g','negative_fraction_ks','rank_residual_corr_radius_cubic_g','rank_residual_corr_radius_cubic_ks']].round(4))
print('g attenuation range:',summary.A_g_full_mag.min(),summary.A_g_full_mag.max())
print('Ks attenuation range:',summary.A_ks_full_mag.min(),summary.A_ks_full_mag.max())''')
md('''## Takeaways
The executed table and plots establish viewing dependence in an ideal simulation with a known dust-free reference. A real galaxy has no observable dust-free twin. Projected dust mass and attenuation are useful diagnostic targets, but their association does not identify the line-of-sight placement of stars and dust, clumping, or a unique 3D distribution. A foreground screen is not justified by these correlations.

Before training: forward-model intensity images with documented or explicitly assumed PSFs, angular scales, sampling and noise; evaluate dust proxies against stellar-brightness/radius baselines. Keep the dust-free twin for evaluation only. Spatial autocorrelation, a single object, and radiative-transfer noise prevent a population-level accuracy claim. See `next_experiments.md` for the instrument-specific plan and `hawki_inspection_report.md` for the independent raw-data audit.''')
n=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'name':'phd','display_name':'Python 3.12 (NTHU Research)','language':'python'}})
nbf.validate(n); nbf.write(n,O/'TNG294866_five_orientations.ipynb')
