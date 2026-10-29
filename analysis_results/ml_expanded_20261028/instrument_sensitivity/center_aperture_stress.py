"""Native-grid paired-label robustness, strictly frozen nonfinal O1 subset."""
from pathlib import Path
import sys,json,os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
import pandas as pd
from scipy.ndimage import shift
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O.parent))
import expanded_features as f

def main():
    selected=pd.read_csv(O/'selected_galaxies.csv')
    partition=pd.read_csv(f.PART).set_index('subhalo_id')
    assert len(selected)==20 and not selected.partition.eq('final_test').any()
    assert all(partition.loc[r.subhalo_id,'partition']==r.partition for r in selected.itertuples())
    rows=[];checks=[];identity=[]
    for row in selected.itertuples():
        sid=int(row.subhalo_id)
        with np.load(O.parent/'data_audit/cache'/str(sid)/'O1.npz') as z:
            clear=np.array([z['clear_'+b] for b in f.SOURCE],dtype=float)
            dusty=np.array([z['dusty_'+b] for b in f.SOURCE],dtype=float)
        assert clear.shape==dusty.shape==(3,800,800)
        radius,_=f.aperture_policy(dusty)
        baseline=f.labels_for(clear,dusty,radius)
        # Independent saved root label product is inspected only for this nonfinal ID.
        saved=O.parent/'derived'/str(sid)/'labels.csv'
        if saved.exists():
            labels=pd.read_csv(saved)
            q=labels[(labels.view=='O1')&(labels.aperture=='adaptive')]
            assert len(q)==1
            err=float(np.max(np.abs(q[f.TARGETS].to_numpy()[0]-np.array([baseline[t] for t in f.TARGETS]))))
            assert err<1e-10
            identity.append(dict(subhalo_id=sid,max_absolute_difference=err))
        cases=[('baseline',radius,0.,0.),('radius_x0.8',radius*.8,0.,0.),
            ('radius_x1.2_cap35',min(35.,radius*1.2),0.,0.),
            ('center_x_plus0.5',radius,.5,0.),('center_x_minus0.5',radius,-.5,0.),
            ('center_y_plus0.5',radius,0.,.5),('center_y_minus0.5',radius,0.,-.5)]
        for case,r,dx,dy in cases:
            c,d=clear,dusty
            if dx or dy:
                # Center +dx,+dy in source coordinates is image translation -dx,-dy.
                offsets=(0.,-dy/.1,-dx/.1)
                c=shift(clear,offsets,order=1,mode='constant',cval=0.,prefilter=False)
                d=shift(dusty,offsets,order=1,mode='constant',cval=0.,prefilter=False)
                # Exact integer sampling: no interpolation mixture or cross-band shift.
                assert all(abs(v-round(v))<1e-12 for v in offsets)
            values=f.labels_for(c,d,r)
            assert np.isfinite([values[t] for t in f.TARGETS]).all()
            # Direct off-center Geometry is an independent sign/centering check.
            geom=f.Geometry(800,.1,r,cx=dx,cy=dy)
            direct={}
            flux_errors=[]
            centered=f.Geometry(800,.1,r)
            for j,band in [(0,'g'),(2,'Ks')]:
                a,b=f.measure(clear[j],geom),f.measure(dusty[j],geom)
                direct['A_'+band]=-2.5*np.log10(b['flux']/a['flux'])
                direct['dR50_'+band]=b['R50']-a['R50']
                direct['dC_'+band]=b['C']-a['C']
                for original,moved in [(clear[j],c[j]),(dusty[j],d[j])]:
                    v1=original[geom.mask].sum();v2=moved[centered.mask].sum()
                    flux_errors.append(abs(v1-v2)/max(abs(v1),1e-30))
            errors={t:abs(values[t]-direct[t]) for t in direct}
            assert max(errors.values())<1e-10
            assert max(flux_errors)<1e-12
            # R35 plus max offset and five-sigma 1-kpc-FWHM smoothing remains inside R40 field.
            smoothing_support=5*(1/.1/2.354820045)*.1
            assert r+abs(dx)+abs(dy)+smoothing_support<40
            checks.append(dict(subhalo_id=sid,case=case,max_direct_geometry_target_difference=max(errors.values()),
                max_pair_aperture_flux_relative_error=max(flux_errors),edge_margin_after_smoothing_kpc=40-r-abs(dx)-abs(dy)-smoothing_support))
            for target in f.TARGETS:
                rows.append(dict(subhalo_id=sid,view='O1',partition=row.partition,case=case,target=target,
                    baseline_radius_kpc=radius,radius_kpc=r,aperture_center_x_kpc=dx,aperture_center_y_kpc=dy,
                    native_pixel_kpc=.1,value=values[target],baseline_value=baseline[target],
                    delta=values[target]-baseline[target],abs_delta=abs(values[target]-baseline[target]),
                    radius_cap_applied=bool(case=='radius_x1.2_cap35' and radius*1.2>35),
                    zero_projected_dust=q.zero_projected_dust.iloc[0] if saved.exists() and 'zero_projected_dust' in q else np.nan))
        print('Center/aperture stress',sid,row.partition,flush=True)
    result=pd.DataFrame(rows);assert len(result)==1120
    result.to_csv(O/'center_aperture_target_changes.csv',index=False)
    result.pivot(index=['subhalo_id','view','partition','case','baseline_radius_kpc','radius_kpc','aperture_center_x_kpc','aperture_center_y_kpc'],columns='target',values='value').reset_index().to_csv(O/'center_aperture_targets_wide.csv',index=False)
    pd.DataFrame(checks).to_csv(O/'center_aperture_numerical_checks.csv',index=False)
    summaries=[]
    for groupname,sub in [('all20',result),('development6',result[result.partition=='development']),('validation14',result[result.partition=='validation'])]:
        for (case,target),g in sub.groupby(['case','target']):
            summaries.append(dict(subset=groupname,case=case,target=target,n_galaxies=len(g),
                median_delta=g.delta.median(),mean_delta=g.delta.mean(),median_abs_delta=g.abs_delta.median(),
                p90_abs_delta=g.abs_delta.quantile(.9),max_abs_delta=g.abs_delta.max(),
                sign_flip_count=int(((g.value*g.baseline_value)<0).sum()),
                sign_flip_caution='strict sign flip only; near-zero controls retained, no significance implied'))
    pd.DataFrame(summaries).to_csv(O/'center_aperture_summary.csv',index=False)
    check=pd.DataFrame(checks)
    verification=dict(passed=True,n_galaxies=len(selected),n_cases=7,n_targets=8,n_rows=len(result),
        n_final_test_rows=int(result.partition.eq('final_test').sum()),nonfinite_target_values=int((~np.isfinite(result.value)).sum()),
        saved_baseline_identity=identity,max_direct_geometry_target_difference=float(check.max_direct_geometry_target_difference.max()),
        max_pair_aperture_flux_relative_error=float(check.max_pair_aperture_flux_relative_error.max()),
        minimum_edge_margin_after_smoothing_kpc=float(check.edge_margin_after_smoothing_kpc.min()),
        radius_cap_galaxies=int(result[result.case=='radius_x1.2_cap35'].drop_duplicates('subhalo_id').radius_cap_applied.sum()),
        units='A and C in magnitudes; R50 in kpc; attenuation IQR in magnitudes',
        labels='Frozen labels_for eight targets; clear/dusty paired with identical shift and aperture; no model updates',
        center_convention='Positive center x/y means aperture moves toward positive original coordinate; images translated oppositely by exactly five native pixels',
        limitations='Native noise-free source labels only, O1 only, selected20 not population; center fixed perturbation not fitted centering uncertainty; radius changes alter enclosed light and attenuation-pixel population; no joint center/radius perturbations, no PSF/noise/feature/model rerun')
    (O/'center_aperture_verification.json').write_text(json.dumps(verification,indent=2))
    print(json.dumps(verification,indent=2))

if __name__=='__main__':main()
