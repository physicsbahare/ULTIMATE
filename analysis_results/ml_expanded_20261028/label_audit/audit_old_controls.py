"""Read only four OLD source-null controls. Never reads expansion images/labels.
Run: python3 analysis_results/ml_expanded_20261028/label_audit/audit_old_controls.py
Minimal primary-HDU FITS reader avoids environment-dependent astropy requirement.
"""
from pathlib import Path
import csv, json, tarfile, re
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
OLD=ROOT/'analysis_results/multigalaxy_morphology_20261027'
IDS=(13,167418,184937,613192)

def fits_primary(raw):
    h={}; end=None
    for p in range(0,len(raw),80):
        s=raw[p:p+80].decode('ascii')
        if s[:8].strip()=='END': end=((p+80+2879)//2880)*2880;break
        if s[8:10]=='= ':
            val=s[10:].strip()
            if val.startswith("'"): val=val[1:val.index("'",1)].strip()
            else:
                val=val.split('/')[0].strip()
                try: val=float(val.replace('D','E')) if any(x in val for x in '.ED') else int(val)
                except ValueError: pass
            h[s[:8].strip()]=val
    assert end is not None and h['NAXIS']==2
    dtype={-32:'>f4',-64:'>f8',16:'>i2',32:'>i4'}[h['BITPIX']]
    a=np.frombuffer(raw,dtype=dtype,count=h['NAXIS1']*h['NAXIS2'],offset=end).reshape(h['NAXIS2'],h['NAXIS1']).astype(float)
    a=a*h.get('BSCALE',1)+h.get('BZERO',0)
    return h,a

def main():
    full=[]; shapes=[]; rawchecks=[]; headers=[]
    yy,xx=np.indices((400,400));mask=(xx-199.5)**2+(yy-199.5)**2 <=120**2
    for sid in IDS:
        fi=pd.read_csv(OLD/'cache'/str(sid)/'fits.csv')
        p=fi[fi.scene.isin(['dusty','clear'])].pivot(index=['view','band'],columns='scene',values='field_sum').reset_index()
        for r in p.to_dict('records'):
            full.append(dict(subhalo_id=sid,view=r['view'],band=r['band'],fullfield_ratio=r['dusty']/r['clear'],fullfield_A_mag=-2.5*np.log10(r['dusty']/r['clear'])))
        for view in ['O1','O2','O3','O4','O5']:
            with np.load(OLD/'cache'/str(sid)/(view+'.npz')) as z:
                for band in ['LSST_g','2MASS_J','2MASS_Ks']:
                    c=z['clear_'+band].astype(float);d=z['dusty_'+band].astype(float)
                    valid=mask&(c>c.max()*1e-4);amp=d[mask].sum()/c[mask].sum()
                    for fw in [0.,.5,1.]:
                        cs=gaussian_filter(c,fw/.1/2.35482) if fw else c
                        ds=gaussian_filter(d,fw/.1/2.35482) if fw else d
                        rr=ds/amp-cs
                        shapes.append(dict(subhalo_id=sid,view=view,band=band,FWHM_kpc=fw,ratio_R12=amp,A_R12_mag=-2.5*np.log10(amp),normalized_shape_RMS=np.sqrt(np.mean(rr[valid]**2)/np.mean(cs[valid]**2)),residual_correlation_with_clear=np.corrcoef(rr[valid],cs[valid])[0,1]))
        path=ROOT/'data/TNG50_SKIRT_DR1_extra'/f'TNG50_DR1_{sid}.tar.gz'
        # Independent raw check of O1 g,J,Ks, plus dust map; all other members skipped.
        with tarfile.open(path,mode='r|gz') as tf:
            for m in tf:
                mt=re.search(r'_O1_(.+)\.fits$',m.name)
                if not mt or mt[1] not in ['LSST_g','LSST_g_nodust','2MASS_J','2MASS_J_nodust','2MASS_Ks','2MASS_Ks_nodust','dustmass']: continue
                key=mt[1];h,a=fits_primary(tf.extractfile(m).read())
                headers.append(dict(subhalo_id=sid,member=m.name,header=h))
                if key=='dustmass':
                    rawchecks.append(dict(subhalo_id=sid,product=key,fullfield_sum=float(a.sum()),nonzero_pixels=int(np.count_nonzero(a))))
                else:
                    scene='clear' if key.endswith('_nodust') else 'dusty'; band=key.removesuffix('_nodust')
                    with np.load(OLD/'cache'/str(sid)/'O1.npz') as z: cached=z[f'{scene}_{band}']
                    orig=fi.loc[fi.member==m.name,'field_sum'].iloc[0]
                    rawchecks.append(dict(subhalo_id=sid,product=key,fullfield_sum=float(a.sum()),inventory_sum_difference=float(a.sum()-orig),cache_crop_max_abs_difference=float(np.max(np.abs(cached-a[600:1000,600:1000]))),cache_exact_equal=bool(np.array_equal(cached,a[600:1000,600:1000])),unit=h.get('BUNIT'),shape=str(a.shape)))
        print('completed old control',sid,flush=True)
    f=pd.DataFrame(full); s=pd.DataFrame(shapes);r=pd.DataFrame(rawchecks)
    f.to_csv(OUT/'old_control_fullfield_ratios.csv',index=False); s.to_csv(OUT/'old_control_spatial_residuals.csv',index=False);r.to_csv(OUT/'raw_cache_checks.csv',index=False)
    (OUT/'raw_headers.json').write_text(json.dumps(headers,indent=2))
    f.groupby('band').agg(n=('fullfield_A_mag','size'),median_A=('fullfield_A_mag','median'),min_A=('fullfield_A_mag','min'),max_A=('fullfield_A_mag','max'),sd_A=('fullfield_A_mag','std')).to_csv(OUT/'cross_band_summary.csv')
    s.groupby(['band','FWHM_kpc']).agg(median_A=('A_R12_mag','median'),median_shape_RMS=('normalized_shape_RMS','median')).to_csv(OUT/'spatial_summary.csv')
    print((OUT/'cross_band_summary.csv').read_text())
if __name__=='__main__':main()
