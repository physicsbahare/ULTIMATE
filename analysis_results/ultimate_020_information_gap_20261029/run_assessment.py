"""Authorized bounded continuation. No canonical drivers, models or final data used.
Run stages separately: --operators, --features, --ml. Each refuses output overwrite.
"""
from pathlib import Path
import sys, json, hashlib, platform, importlib.metadata
import numpy as np
import pandas as pd
from scipy import signal
from scipy.special import erf
from sklearn.model_selection import KFold

O=Path(__file__).resolve().parent
ROOT=O.parents[1]
S=O.parent/'ml_expanded_20261028'
sys.path.insert(0,str(S))
import expanded_features as e
import expanded_models as models
from morphology import Geometry,measure
BETA=3.0208050586423507
WIDTHS={'w039':.38955078125,'w020':.2}
TARGETS=['A_g','A_Ks','dR50_Ks','dC_Ks']
IDS=[13,96763,184931,294866,448830,521429,535051,576516,578834,589873,594731,626408,630760,638950]
SEED=20261029


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def width_parameters(width,family):
    if family=='gaussian':return width/2.354820045,width
    alpha=width/(2*np.sqrt(2**(1/BETA)-1))
    return alpha,2*alpha*np.sqrt(2**(1/(BETA-1))-1)


def kernel(width,pixel,family,quadrature=2):
    scale,_=width_parameters(width,family)
    half=int(np.ceil((6 if family=='gaussian' else 30)*scale/pixel))
    axis=np.arange(-half,half+1)*pixel
    y,x=np.meshgrid(axis,axis,indexing='ij')
    k=np.zeros_like(x)
    for dy in (np.arange(quadrature)+.5)/quadrature-.5:
        for dx in (np.arange(quadrature)+.5)/quadrature-.5:
            rr=(x+dx*pixel)**2+(y+dy*pixel)**2
            k+=np.exp(-.5*rr/scale**2) if family=='gaussian' else (1+rr/scale**2)**(-BETA)
    return k/k.sum()


def point_check(width,family,native,phase,refinement=2):
    native=native/refinement
    k=kernel(width,native,family,2)
    n=len(k);edges=(np.arange(n+1)-n/2)*native
    m=2*int(np.ceil((abs(edges[0])+.2)/.1))
    out=(np.arange(m+1)-m/2)*.1+phase
    sampled=e.old.p.overlap_flux(k,edges,out)
    scale,d50=width_parameters(width,family)
    if family=='gaussian':
        v=.5*np.diff(erf(out/(np.sqrt(2)*scale)))
        analytic=np.outer(v,v)
    else:
        centers=(out[1:]+out[:-1])/2
        y,x=np.meshgrid(centers,centers,indexing='ij');analytic=np.zeros_like(x)
        for dy in (np.arange(20)+.5)/20-.5:
            for dx in (np.arange(20)+.5)/20-.5:
                analytic+=(1+((x+dx*.1)**2+(y+dy*.1)**2)/scale**2)**(-BETA)
        analytic*=.1**2/400*(BETA-1)/(np.pi*scale**2)
    return dict(check='point_analytic',family=family,FWHM_arcsec=width,D50_arcsec=d50,
        native_pixel_arcsec=native,detector_pixel_arcsec=.1,phase_x_arcsec=phase,phase_y_arcsec=phase,
        kernel_sum=float(k.sum()),kernel_min=float(k.min()),detector_flux=float(sampled.sum()),
        relative_L1_analytic=float(abs(sampled-analytic).sum()/analytic.sum()),
        peak_pixel=float(sampled.max()),
        analytic_tail_outside_30alpha=(1+30**2)**(1-BETA) if family=='moffat' else 0.)


def make_folds(ids):
    ids=np.array(sorted(ids));rows=[]
    for fold,(_,test) in enumerate(KFold(5,shuffle=True,random_state=SEED).split(ids)):
        rows.extend(dict(subhalo_id=int(i),fold=fold) for i in ids[test])
    return pd.DataFrame(rows)


def render(scene,family,width,q=2,refinement=2):
    g=e.geometry('glao');g['widths']=g['widths'].copy();g['widths'][2]=width
    # Reuse the original operator for g/J. Replace Ks only with subdivided
    # constant source cells, native radiometry and the same exact area overlaps.
    rate,loss=e.old.p.render(scene,g)
    native=g['native']/refinement
    flux=np.pad(scene[2],80)/(1+g['z'])**3*1e6*(g['native']/e.old.p.ARCSEC_PER_RAD)**2
    before=flux.sum()
    flux=np.repeat(np.repeat(flux,refinement,axis=0),refinement,axis=1)/refinement**2
    conv=signal.fftconvolve(flux,kernel(width,native,family,q),mode='same')
    n=conv.shape[0];edges=(np.arange(n+1)-n/2)*native
    full=e.old.p.overlap_flux(conv,edges,g['outedges'])
    kloss=abs(1-full.sum()/before)
    rate[2]=np.maximum(full[g['sl'],g['sl']],0)*e.old.p.INST[2]['flat_e_s_per_jy']
    return rate,max(loss,kloss),g


def read_pair(sid,view):
    assert sid in IDS
    with np.load(S/'data_audit/cache'/str(sid)/(view+'.npz')) as z:
        return tuple(np.array([z[k+'_'+b] for b in e.SOURCE],dtype=float) for k in ['clear','dusty'])


def load_labels():
    # Read only subset-specific saved development labels, not mixed-partition tables.
    labels=pd.concat([pd.read_csv(S/'derived'/str(i)/'labels.csv') for i in IDS],ignore_index=True)
    labels=labels[labels.aperture=='adaptive'].copy()
    assert set(labels.partition)=={'development'}
    assert set(labels.loc[labels.zero_projected_dust,'subhalo_id'])=={13}
    return labels


def operators():
    assert not (O/'psf_definition_and_operator_checks.csv').exists(),'New directory required to rerun'
    meta=pd.read_csv(e.PART);chosen=meta[meta.subhalo_id.isin(IDS)].copy()
    assert len(chosen)==14 and set(chosen.partition)=={'development'}
    controls={13,167418,184937,613192,319734,208821,184946,117296,96767,63884,184945,338448}
    dev=meta[(meta.partition=='development')&~meta.subhalo_id.isin(controls)].sort_values(['log10_stellar_mass','subhalo_id'])
    assert set(dev.iloc[[round(i*(len(dev)-1)/11) for i in range(12)]].subhalo_id)|{13,294866}==set(IDS)
    chosen.to_csv(O/'selected_galaxies.csv',index=False)
    labels=load_labels();labels.to_csv(O/'subset_saved_labels.csv',index=False)
    folds=make_folds([i for i in IDS if i!=13]);folds.to_csv(O/'galaxy_folds.csv',index=False)
    files=[e.PART,Path(e.__file__),Path(models.__file__),Path(e.old.__file__),Path(e.old.p.__file__),
        O.parent/'screen_test_20261026/forward_physics.py',O.parent/'multigalaxy_morphology_20261027/morphology.py',
        O.parent/'hawki_m4off_20261028/PSF_summary.csv',O/'overlap_and_novelty_audit.md',O/'experiment_protocol.md',Path(__file__)]
    for sid in IDS:
        files.append(S/'derived'/str(sid)/'labels.csv')
        files.extend(S/'data_audit/cache'/str(sid)/(v+'.npz') for v in ['O1','O2','O3','O4','O5'])
    g=e.geometry('glao')
    provenance=dict(date='2026-10-29 Asia/Taipei',python=sys.executable,version=platform.python_version(),
        packages={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','astropy','scikit-learn','matplotlib']},
        inputs=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p)) for p in files],
        scale_kpc_per_arcsec=g['scale'],native_pixel_kpc=.1,native_pixel_arcsec=g['native'],
        angular_diameter_distance_Mpc=g['scale']*206264.80624709636/1000,
        pixel_kpc=g['pixel']*g['scale'],z=.1,noise='none',seeds=dict(folds=SEED,bootstrap=SEED),
        final_inference_count=0,validation_accessed=False)
    (O/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    rows=[]
    for family in ['gaussian','moffat']:
        for width in WIDTHS.values():
            for phase in [0.,.05]:
                row=point_check(width,family,g['native'],phase)
                assert row['relative_L1_analytic']<.02 and abs(row['detector_flux']-1)<1e-4,row
                rows.append(row)
            coarse=point_check(width,family,g['native'],0.,refinement=1)
            coarse['check']='coarse_grid_diagnostic';rows.append(coarse)
    clear,dusty=read_pair(13,'O1');radius=float(labels[(labels.subhalo_id==13)&(labels.view=='O1')].radius_kpc.iloc[0])
    for family in ['gaussian','moffat']:
        for width in WIDTHS.values():
            a,loss,geom=render(dusty,family,width,2);b,loss4,_=render(dusty,family,width,4,4)
            mg=Geometry(geom['shape'][0],geom['pixel']*geom['scale'],radius)
            ma,mb=measure(a[2],mg),measure(b[2],mg)
            row=dict(check='quadrature_control13_O1',family=family,FWHM_arcsec=width,
                D50_arcsec=width_parameters(width,family)[1],quadrature_coarse=2,quadrature_fine=4,grid_refinement_coarse=2,grid_refinement_fine=4,
                R50_change_kpc=mb['R50']-ma['R50'],C_change=mb['C']-ma['C'],
                relative_L1_image=float(abs(a[2]-b[2]).sum()/b[2].sum()),padded_flux_loss=max(loss,loss4))
            rows.append(row)
            assert abs(row['R50_change_kpc'])<.03 and abs(row['C_change'])<.03 and row['padded_flux_loss']<1e-4,row
            if family=='gaussian':
                old,oldloss=e.old.p.render(dusty,geom)
                mo=measure(old[2],mg)
                rows.append(dict(check='legacy_vs_integrated_control13_O1',family=family,FWHM_arcsec=width,
                    R50_change_kpc=ma['R50']-mo['R50'],C_change=ma['C']-mo['C'],
                    relative_L1_image=float(abs(old[2]-a[2]).sum()/a[2].sum()),padded_flux_loss=oldloss))
    pd.DataFrame(rows).to_csv(O/'psf_definition_and_operator_checks.csv',index=False)
    print('Operator checks passed; scale',g['scale'],'native arcsec',g['native'],flush=True)


def features():
    assert (O/'psf_definition_and_operator_checks.csv').exists()
    assert not (O/'observable_features.csv.gz').exists(),'Refuse overwrite'
    labels=pd.read_csv(O/'subset_saved_labels.csv');fr=[];mr=[];checks=[]
    for sid in IDS:
        for view in ['O1','O2','O3','O4','O5']:
            clear,dusty=read_pair(sid,view)
            lab=labels[(labels.subhalo_id==sid)&(labels.view==view)].iloc[0]
            for family in ['gaussian','moffat']:
                for condition,width in WIDTHS.items():
                    d,dloss,g=render(dusty,family,width);c,closs,_=render(clear,family,width)
                    assert max(dloss,closs)<1e-4
                    info=dict(subhalo_id=sid,view=view,family=family,condition=condition,source_control=sid==13)
                    plan=e.FeaturePlan(g,lab.radius_kpc)
                    f=plan(d);assert np.isfinite(list(f.values())).all()
                    fr.append(dict(**info,**f))
                    for metric in ['R50','C']:
                        observed=measure(d[2],plan.m)[metric];paired=observed-measure(c[2],plan.m)[metric]
                        native=lab['dusty_'+metric+'_Ks'];truth=lab['d'+metric+'_Ks']
                        mr.append(dict(**info,metric=metric,native_dusty=native,observed_dusty=observed,
                            native_pair_difference=truth,observed_pair_difference=paired,
                            morphology_signed_error=observed-native,morphology_abs_error=abs(observed-native),
                            pair_transfer_signed_error=paired-truth,pair_transfer_abs_error=abs(paired-truth)))
                    checks.append(dict(**info,padded_flux_loss=max(dloss,closs)))
        print('Features/morphology complete:',sid,flush=True)
    pd.DataFrame(fr).to_csv(O/'observable_features.csv.gz',index=False)
    pd.DataFrame(mr).to_csv(O/'morphology_resolution_results.csv',index=False)
    pd.DataFrame(checks).to_csv(O/'render_checks.csv',index=False)
    f=pd.DataFrame(fr);changes=[];gates=[]
    for family,part in f.groupby('family'):
        p=part.pivot(index=['subhalo_id','view'],columns='condition',values='Ks_texture_0.5')
        v=(abs(p.w020-p.w039)/abs(p.w039).clip(lower=1e-12)).groupby('subhalo_id').mean()
        for sid,val in v.items():changes.append(dict(family=family,subhalo_id=sid,mean_absolute_fractional_texture_change=val,source_control=sid==13))
        v=v.drop(13);gates.append(dict(family=family,median_galaxy_fractional_change=float(v.median()),n_exceed_1percent=int((v>.01).sum()),n_galaxies=len(v),passed=bool(v.median()>.01 and (v>.01).sum()>=len(v)/2)))
    pd.DataFrame(changes).to_csv(O/'observable_changes.csv',index=False)
    (O/'phase2_gate.json').write_text(json.dumps(dict(criteria='Prespecified >1% texture change in median and at least half galaxies; not target information proof',families=gates,proceed_ml=all(x['passed'] for x in gates)),indent=2)+'\n')
    print(gates,flush=True)


def ci(values):
    v=np.asarray(values,float);rng=np.random.default_rng(SEED)
    boot=v[rng.integers(0,len(v),(5000,len(v)))].mean(axis=1)
    return float(np.quantile(boot,.025)),float(np.quantile(boot,.975))


def ml():
    assert json.loads((O/'phase2_gate.json').read_text())['proceed_ml']
    assert not (O/'ml_predictions.csv.gz').exists(),'Refuse overwrite'
    f=pd.read_csv(O/'observable_features.csv.gz');y=pd.read_csv(O/'subset_saved_labels.csv')
    folds=pd.read_csv(O/'galaxy_folds.csv')
    data=f.merge(y[['subhalo_id','view']+TARGETS],on=['subhalo_id','view'],validate='many_to_one')
    rows=[]
    for family in ['gaussian','moffat']:
        part=data[data.family==family]
        for model in ['phot_ridge','summary_ridge','spatial_ridge']:
            for train_condition in WIDTHS:
                for fold in range(5):
                    testids=folds.loc[folds.fold==fold,'subhalo_id'];trainids=folds.loc[folds.fold!=fold,'subhalo_id']
                    assert not set(testids)&set(trainids)
                    train=part[(part.condition==train_condition)&part.subhalo_id.isin(trainids)]
                    estimator=models.model(dict(family=model,value=10),'GLAO_NIR')
                    # Legacy model API supports this target subset without source/truth features.
                    estimator.fit(train,train[TARGETS])
                    for test_condition in WIDTHS:
                        test=part[(part.condition==test_condition)&(part.subhalo_id.isin(testids)|part.source_control)]
                        pred=estimator.predict(test)
                        for j,target in enumerate(TARGETS):
                            r=test[['subhalo_id','view','source_control']].copy()
                            r['family']=family;r['model']=model;r['fold']=fold
                            r['train_condition']=train_condition;r['test_condition']=test_condition
                            r['evaluation']='resolution_specific' if test_condition==train_condition else 'fixed_model_transfer'
                            r['target']=target;r['truth']=test[target].to_numpy();r['prediction']=pred[:,j]
                            r['signed_error']=r.prediction-r.truth;r['abs_error']=abs(r.signed_error)
                            rows.append(r)
            print('ML held-out folds complete:',family,model,flush=True)
    pred=pd.concat(rows,ignore_index=True);pred.to_csv(O/'ml_predictions.csv.gz',index=False)
    primary=pred[~pred.source_control]
    keys=['family','model','train_condition','test_condition','evaluation','target']
    galaxy=primary.groupby(keys+['subhalo_id'],as_index=False)[['abs_error','signed_error']].mean()
    galaxy.to_csv(O/'galaxy_level_ml_errors.csv',index=False)
    # Controls are fold-ensemble diagnostics, distinct from primary CV.
    controls=pred[pred.source_control].groupby(keys+['subhalo_id','view'],as_index=False)[['truth','prediction']].mean()
    controls['signed_error']=controls.prediction-controls.truth
    controls.to_csv(O/'source_control_predictions.csv',index=False)
    scores=[]
    for vals,p in galaxy.groupby(keys):
        lo,hi=ci(p.abs_error);scores.append(dict(zip(keys,vals),MAE=p.abs_error.mean(),MAE_lo=lo,MAE_hi=hi,n_galaxies=len(p)))
    score=pd.DataFrame(scores)
    specific=galaxy[galaxy.evaluation=='resolution_specific']
    increments=[];changes=[]
    for (family,target),p in specific.groupby(['family','target']):
        photo=p[p.model=='phot_ridge'].pivot(index='subhalo_id',columns='test_condition',values='abs_error')
        for model in ['phot_ridge','summary_ridge','spatial_ridge']:
            v=p[p.model==model].pivot(index='subhalo_id',columns='test_condition',values='abs_error')
            gain=v.w039-v.w020
            incremental=(photo.w020-v.w020)-(photo.w039-v.w039)
            for sid in v.index:
                changes.append(dict(family=family,target=target,model=model,subhalo_id=sid,
                    MAE_w039=v.loc[sid,'w039'],MAE_w020=v.loc[sid,'w020'],paired_width_gain=gain.loc[sid],
                    incremental_spatial_gain_w039=photo.loc[sid,'w039']-v.loc[sid,'w039'],
                    incremental_spatial_gain_w020=photo.loc[sid,'w020']-v.loc[sid,'w020'],
                    change_in_incremental_gain=incremental.loc[sid]))
            glo,ghi=ci(gain);ilo,ihi=ci(incremental)
            for condition in WIDTHS:
                inc=photo[condition]-v[condition];lo,hi=ci(inc)
                increments.append(dict(family=family,target=target,model=model,test_condition=condition,
                    photometric_MAE=photo[condition].mean(),incremental_MAE=inc.mean(),incremental_lo=lo,incremental_hi=hi,
                    paired_width_gain=gain.mean(),paired_width_gain_lo=glo,paired_width_gain_hi=ghi,
                    change_in_incremental_gain=incremental.mean(),change_in_incremental_gain_lo=ilo,change_in_incremental_gain_hi=ihi))
    score=score.merge(pd.DataFrame(increments),on=['family','target','model','test_condition'],how='left',validate='many_to_one')
    # Incremental columns apply only to matched resolution-specific estimators.
    cols=[c for c in score if c not in keys+['MAE','MAE_lo','MAE_hi','n_galaxies']]
    score.loc[score.evaluation!='resolution_specific',cols]=np.nan
    score.to_csv(O/'ml_information_gain_results.csv',index=False)
    pd.DataFrame(changes).to_csv(O/'galaxy_level_uncertainties.csv',index=False)
    print('ML complete; 13 independent primary galaxies, five views each; no tuning',flush=True)


if __name__=='__main__':
    if '--operators' in sys.argv:operators()
    elif '--features' in sys.argv:features()
    elif '--ml' in sys.argv:ml()
    else:raise SystemExit('Choose --operators, --features or --ml explicitly')
