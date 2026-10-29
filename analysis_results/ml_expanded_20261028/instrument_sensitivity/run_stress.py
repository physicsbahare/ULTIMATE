"""O1-only instrument sensitivities: frozen observable features, no fitting or labels."""
from pathlib import Path
import os, sys, json, hashlib, time
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
import pandas as pd
from scipy.ndimage import convolve1d

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
sys.path.insert(0,str(ROOT))
import expanded_features as f
HAWKI=ROOT.parent/'ml_feasibility_20261027/hawki'
EMP=json.loads((HAWKI/'empirical_model_inputs.json').read_text())
CAT=json.loads((HAWKI/'catalogue_validation_summary.json').read_text())
BETA=CAT['quality_matched_psf']['beta']['median']

def local_kernel(rho):
    a=(1-np.sqrt(1-2*rho*rho))/(2*rho)
    k=np.array([a,1.,a]);return k/np.sqrt(np.sum(k*k))

KX=local_kernel(EMP['background']['rho_adjacent_x'])
KY=local_kernel(EMP['background']['rho_adjacent_y'])

def correlate(e):
    z=e.copy()
    z[2]=convolve1d(convolve1d(e[2],KX,axis=1,mode='wrap'),KY,axis=0,mode='wrap')
    return z

def bin2(a):
    b,c=a.shape[-2:];assert b%2==c%2==0
    return a.reshape(*a.shape[:-2],b//2,2,c//2,2).sum(axis=(-3,-1))

def bin_geometry(g):
    z=g.copy();n=g['shape'][0]//2
    xy=(np.arange(n)+.5-n/2)*.2*g['scale']
    y,x=np.meshgrid(xy,xy,indexing='ij')
    z.update(pixel=.2,shape=(n,n),x=x,y=y,r=np.hypot(x,y),roi=np.hypot(x,y)<30)
    assert np.isclose(n*z['pixel'],g['shape'][0]*g['pixel'])
    assert np.allclose(x,bin2(g['x'][None])[0]/4)
    return z

def render_wings(dusty,g):
    original=f.old.p.psf_kernel
    def kernel(width,pixel,kind):
        if abs(width-g['widths'][2])>1e-9:return original(width,pixel,kind)
        alpha=width/(2*np.sqrt(2**(1/(BETA-1))-1))/pixel
        axis=np.arange(-int(np.ceil(12*alpha)),int(np.ceil(12*alpha))+1)
        y,x=np.meshgrid(axis,axis,indexing='ij')
        k=(1+(x*x+y*y)/alpha**2)**(-BETA);k/=k.sum()
        assert np.isclose(k.sum(),1,atol=1e-14)
        return k
    try:
        f.old.p.psf_kernel=kernel
        return f.old.p.render(dusty,g)
    finally:f.old.p.psf_kernel=original

def manifest():
    rows=[]
    logs=json.loads((HAWKI/'reduced_download_log.json').read_text())
    for row in logs:
        p=Path(row['path']);sha=hashlib.sha256(p.read_bytes()).hexdigest()
        assert sha==row['sha256'] and p.stat().st_size==row['bytes']
        rows.append(dict(role=row['category'],original_path=str(p),bytes=p.stat().st_size,
            sha256=sha,archive_id=row['dp_id'],source_url=row['url'],
            citation='ESO HAWK-I imaging pipeline processed data; DOI 10.18727/archive/34; programme 60.A-9475(A)',
            scope=row['region'],transfer_status='manifest only; no copy, package or transfer'))
    downloads=json.loads((HAWKI/'catalogue_download_log.json').read_text())
    for name,role in [('associated_photcal.fits','PHOTCAL_TAB'),('eso_jan6_source_catalogue.fits','reduced source catalogue'),('irsa_2mass.csv','2MASS PSC reference')]:
        p=HAWKI/name;row=next(r for r in downloads if r['name']==name)
        rows.append(dict(role=role,original_path=str(p),bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(),archive_id=row['url'].split('/')[-1] if name.endswith('.fits') else 'IRSA fp_psc',
            source_url=row['url'],citation='ESO DOI 10.18727/archive/34; 2MASS All-Sky PSC (Skrutskie et al. 2006)',
            scope='existing small calibration/reference product',transfer_status='manifest only; no copy, package or transfer'))
    pd.DataFrame(rows).to_csv(OUT/'hawki_sharing_manifest.csv',index=False)

def run():
    manifest()
    meta=pd.read_csv(f.PART)
    selected=pd.concat([meta[meta.partition=='development'].head(6),meta[meta.partition=='validation']])
    assert len(selected)==20 and not (selected.partition=='final_test').any()
    selected[['subhalo_id','partition']].to_csv(OUT/'selected_galaxies.csv',index=False)
    epsilon=np.random.default_rng(919).normal(size=(3,1000,1000));noise=correlate(epsilon)[2]
    vx=float(noise.var());rx=float(np.corrcoef(noise[:,:-1].ravel(),noise[:,1:].ravel())[0,1]);ry=float(np.corrcoef(noise[:-1].ravel(),noise[1:].ravel())[0,1])
    assert abs(vx-1)<.01 and abs(rx-EMP['background']['rho_adjacent_x'])<.01 and abs(ry-EMP['background']['rho_adjacent_y'])<.01
    settings=dict(scope='O1-only conditional instrument sensitivity; no model fit, retuning, label access or final-test science',
        development_selection='first six in frozen CSV, including controls; no qualitative tuning',cases=dict(A='Gaussian baseline; provisional rates and diagonal variance',B='Ks circular Moffat beta from nine quality-matched stars; equal D50',C='B plus Ks unit-variance separable local innovation filter',D='software 2x2 sum of A images and native diagonal variances'),
        beta=BETA,beta_stellar_n=9,beta_stellar_IQR=[CAT['quality_matched_psf']['beta'][k] for k in ['p25','p75']],
        beta_full_unconfirmed_candidates=EMP['psf']['beta']['median'],beta_full_n=103,
        beta_caution='Nine-star subset is small and selected; full 103 isolated compact candidates are not all confirmed stars. Medians differ; neither is a universal PSF calibration.',
        retained_D50_arcsec={m:f.geometry(m)['widths'].tolist() for m in ['seeing','glao']},
        psf_caution='Measured HAWK-I FWHM is not equated to ULTIMATE; retain provisional Gaussian-equivalent D50 values.',
        field_assumption='Circular spatially invariant PSFs across each entire image; no anisotropy, field dependence or PSF estimation errors.',
        rho_target_x=EMP['background']['rho_adjacent_x'],rho_target_y=EMP['background']['rho_adjacent_y'],
        local_filter_Kx=KX.tolist(),local_filter_Ky=KY.tolist(),innovation_variance=vx,simulated_rho_x=rx,simulated_rho_y=ry,
        correlation_limit='Local separable MA(2) covariance only (zero beyond two pixels along an axis); wrap boundaries outside aperture. Not a full sky model; does not reproduce real large-aperture excess sky variance or long-range residuals. Filter applies to total Ks innovation; no measured source/sky covariance decomposition.',
        binning='Software sum only, 0.1 to 0.2 arcsec. Same footprint and center. Sum all four source/background/dark/read variance contributions; never call detector variance formula at coarse sampling. Assumes known independent native pixels for case D; no new detector or on-chip read-noise benefit.',
        noise='1h each band; inherited source/background/dark/read Gaussian variance. Same native standard normal innovations for all cases and both modes; D sums exactly case A noisy pixels.',
        aperture='Frozen common seeing dusty-Ks adaptive function; same radius all cases/modes; no clear input',
        features='Exactly expanded_features.FeaturePlan; all cases adaptive/nominal; 4 paired draws',
        source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(f.__file__),f.PART,HAWKI/'empirical_model_inputs.json',HAWKI/'catalogue_validation_summary.json']})
    (OUT/'assumptions.json').write_text(json.dumps(settings,indent=2))
    complete={};valid=[];apertures=[]
    while len(complete)<len(selected):
        for row in selected.itertuples():
            sid=int(row.subhalo_id)
            if sid in complete:continue
            cache=ROOT/'data_audit/cache'/str(sid)/'O1.npz'
            if not cache.exists():continue
            with np.load(cache) as z:dusty=np.array([z['dusty_'+b] for b in f.SOURCE],dtype=float)
            radius,flags=f.aperture_policy(dusty)
            apertures.append(dict(subhalo_id=sid,view='O1',radius_kpc=radius,**flags))
            rates={};vars={};plans={};gg={m:f.geometry(m) for m in ['seeing','glao']}
            for mode,g in gg.items():
                plans[mode]=f.FeaturePlan(g,radius);plans[mode+'D']=f.FeaturePlan(bin_geometry(g),radius)
                for case,renderer in [('A',f.old.p.render),('B',render_wings)]:
                    rate,loss=renderer(dusty,g);assert loss<1e-5
                    rates[case,mode]=rate;vars[case,mode]=f.old.p.variance(rate,1.)
                    valid.append(dict(subhalo_id=sid,mode=mode,case=case,padded_flux_loss=loss))
                r=rates['A',mode];v=vars['A',mode]
                assert np.allclose(bin2(r).sum(axis=(1,2)),r.sum(axis=(1,2)))
                assert np.allclose(bin2(v).sum(axis=(1,2)),v.sum(axis=(1,2)))
                valid.append(dict(subhalo_id=sid,mode=mode,case='D',flux_sum_relative_error=float(np.max(np.abs(bin2(r).sum(axis=(1,2))/r.sum(axis=(1,2))-1))),variance_sum_relative_error=float(np.max(np.abs(bin2(v).sum(axis=(1,2))/v.sum(axis=(1,2))-1)))))
            rng=np.random.default_rng(20261028+sid*101+1000003);rows=[]
            for draw in range(4):
                e=rng.normal(size=rates['A','seeing'].shape);ec=correlate(e)
                for mode in gg:
                    base=rates['A',mode]+np.sqrt(vars['A',mode])*e
                    images=dict(A=base,B=rates['B',mode]+np.sqrt(vars['B',mode])*e,
                        C=rates['B',mode]+np.sqrt(vars['B',mode])*ec,D=bin2(base))
                    for case,image in images.items():
                        plan=plans[mode+'D'] if case=='D' else plans[mode]
                        rows.append(dict(subhalo_id=sid,view='O1',draw=draw,partition=row.partition,
                            aperture='adaptive',condition='nominal',mode=mode,case=case,**plan(image)))
            complete[sid]=pd.DataFrame(rows)
            pd.concat(complete.values(),ignore_index=True).to_csv(OUT/'stress_features.csv.gz',index=False)
            pd.DataFrame(valid).to_csv(OUT/'render_validation.csv',index=False)
            pd.DataFrame(apertures).to_csv(OUT/'apertures.csv',index=False)
            (OUT/'status.json').write_text(json.dumps(dict(complete_ids=list(complete),n_selected=len(selected),n_complete=len(complete),complete=len(complete)==len(selected)),indent=2))
            print('Instrument stress',sid,row.partition,len(complete),'/',len(selected),flush=True)
        if len(complete)<len(selected):time.sleep(15)
    features=pd.concat(complete.values(),ignore_index=True)
    assert len(features)==640 and features.groupby(['subhalo_id','case','mode']).size().eq(4).all()
    (OUT/'feature_schema.json').write_text(json.dumps(dict(columns=features.columns.tolist(),n_rows=len(features),n_feature_columns=len(features.columns)-8),indent=2))

if __name__=='__main__':run()
