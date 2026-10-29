"""Interpretable grouped development selection, untouched validation calibration."""
from pathlib import Path
import json,hashlib,time
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer,TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor,HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import KFold
from sklearn.base import BaseEstimator,RegressorMixin
from expanded_features import O,TARGETS

SCENARIOS=['optical','seeing_NIR','GLAO_NIR']
FAMILIES=['median','screen','phot_ridge','summary_ridge','spatial_ridge','summary_forest','spatial_forest','spatial_boost']


def candidates():
    result=[dict(family='median',value=0),dict(family='screen',value=0)]
    for family in ['phot_ridge','summary_ridge','spatial_ridge']:
        result += [dict(family=family,value=a) for a in [1,10,100]]
    for family in ['summary_forest','spatial_forest']:
        result += [dict(family=family,value=d) for d in [4,8]]
    result += [dict(family='spatial_boost',value=d) for d in [2,3]]
    return result


def name(config):return config['family']+'_'+str(config['value'])


def columns(scenario,family):
    nir=scenario!='optical';bands=['g','J','Ks'] if nir else ['g']
    phot=['g_logJy']+(['color_g_J','color_J_Ks'] if nir else [])
    summary=phot+[b+'_'+m for b in bands for m in ['R50','C','A','q']]
    if nir:summary+=['gradient_g_J','gradient_J_Ks']
    spatial=[f'{b}_radial{k}' for b in bands for k in range(4)]
    spatial += [f'{b}_harmonic{k}' for b in bands for k in [1,2,4]]
    spatial += [f'{b}_texture_{size}' for b in ['g','Ks'] if b in bands for size in [.5,1.,2.]]
    cells=[f'cell_{b}_{k:02d}' for b in ['g','Ks'] if b in bands for k in range(64)]
    if family in ['median','screen','phot_ridge']:return phot,[]
    if family.startswith('summary'):return summary,[]
    return summary+spatial,cells


class ScreenColor(BaseEstimator,RegressorMixin):
    """Fixed lambda^-1 screen slope, fitted population intercept; not geometry inference."""
    def fit(self,X,y):
        self.median_=np.median(y,axis=0)
        self.ratio_=.482/2.159
        self.intercept_=np.median(np.asarray(X)[:,1:3].sum(axis=1)-np.asarray(y)[:,0]*(1-self.ratio_)) if np.shape(X)[1]>1 else 0.
        return self
    def predict(self,X):
        result=np.tile(self.median_,(len(X),1))
        if np.shape(X)[1]>1:
            ag=(np.asarray(X)[:,1:3].sum(axis=1)-self.intercept_)/(1-self.ratio_)
            result[:,0]=ag;result[:,1]=ag*self.ratio_
        return result


def model(config,scenario):
    family=config['family'];base,cells=columns(scenario,family)
    if family=='screen':
        return make_pipeline(ColumnTransformer([('phot',SimpleImputer(strategy='median'),base)]),ScreenColor())
    numeric=make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler())
    transformers=[('summary',numeric,base)]
    if cells:
        transformers.append(('cells',make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler(),PCA(n_components=8,svd_solver='full')),cells))
    if family=='median':regressor=DummyRegressor(strategy='median')
    elif family.endswith('ridge'):regressor=Ridge(alpha=config['value'])
    elif family.endswith('forest'):regressor=RandomForestRegressor(n_estimators=100,max_depth=config['value'],min_samples_leaf=20,random_state=20261028,n_jobs=1)
    else:regressor=MultiOutputRegressor(HistGradientBoostingRegressor(max_iter=100,max_depth=config['value'],learning_rate=.05,l2_regularization=10,min_samples_leaf=20,early_stopping=False,random_state=20261028),n_jobs=1)
    return TransformedTargetRegressor(regressor=make_pipeline(ColumnTransformer(transformers),regressor),transformer=StandardScaler())


def frame(scenario,aperture='adaptive',condition='nominal',partitions=None):
    prefix='final_' if partitions==['final_test'] else ''
    if prefix:assert (O/'FINAL_PROTOCOL_FROZEN.json').exists()
    features=pd.read_csv(O/(prefix+'feature_table.csv.gz'))
    labels=pd.read_csv(O/(prefix+'target_table.csv'))
    mode='glao' if scenario=='GLAO_NIR' else 'seeing'
    x=features[(features.aperture==aperture)&(features.condition==condition)&(features['mode']==mode)]
    if partitions is not None:x=x[x.partition.isin(partitions)]
    joined=x.merge(labels,on=['subhalo_id','view','partition','aperture'],validate='many_to_one')
    return joined


def split_development(labels):
    ids=np.sort(labels[(labels.partition=='development')&~labels.zero_projected_dust].subhalo_id.unique())
    records=[]
    for fold,(fit,test) in enumerate(KFold(5,shuffle=True,random_state=20261028).split(ids)):
        for role,indices in [('fit',fit),('test',test)]:
            records.extend(dict(fold=fold,role=role,subhalo_id=int(sid)) for sid in ids[indices])
    table=pd.DataFrame(records);table.to_csv(O/'development_group_folds.csv',index=False)
    return table


def prediction_rows(frame,prediction,**info):
    rows=[]
    for j,target in enumerate(TARGETS):
        piece=frame[['subhalo_id','view','draw','partition','zero_projected_dust','radius_kpc','reference_aperture_limited','log_stellar_mass','SFR_Msun_yr','dust_mass_field_Msun']].copy()
        piece['target']=target;piece['truth']=frame[target].to_numpy();piece['prediction']=prediction[:,j]
        piece['error']=piece.prediction-piece.truth;piece['abs_error']=abs(piece.error)
        piece['square_error']=piece.error**2
        piece['observed_Ks_q']=frame.Ks_q.to_numpy()
        piece['observable_Ks_logSB']=frame.Ks_logJy.to_numpy()-np.log10(np.pi*(frame.radius_kpc.to_numpy()/1.844278910985618)**2)
        for key,value in info.items():piece[key]=value
        if target.startswith('dR50_') or target.startswith('dC_'):
            metric,band=target[1:].split('_');observed=frame[band+'_'+metric].to_numpy();clear=frame['clear_'+metric+'_'+band].to_numpy()
            piece['uncorrected_error']=observed-clear;piece['corrected_error']=observed-prediction[:,j]-clear
        else:piece['uncorrected_error']=np.nan;piece['corrected_error']=np.nan
        rows.append(piece)
    return pd.concat(rows,ignore_index=True)


def select():
    while not (O/'FEATURE_PREPARATION_COMPLETED.json').exists():time.sleep(5)
    labels=pd.read_csv(O/'target_table.csv');folds=split_development(labels)
    assert labels.groupby('partition').subhalo_id.nunique().loc[['development','validation']].to_dict()=={'development':86,'validation':14}
    assert (O/'label_audit/quality_policy.json').exists()
    destination=O/'cv_checkpoints';destination.mkdir(exist_ok=True)
    scores=[]
    for scenario in SCENARIOS:
        data=frame(scenario,partitions=['development']);data=data[~data.zero_projected_dust]
        for config in candidates():
            path=destination/f'{scenario}_{name(config)}.csv.gz'
            if path.exists():record=pd.read_csv(path)
            else:
                records=[]
                for fold,roles in folds.groupby('fold'):
                    fitids=roles.loc[roles.role=='fit','subhalo_id'];testids=roles.loc[roles.role=='test','subhalo_id']
                    train=data[data.subhalo_id.isin(fitids)];test=data[data.subhalo_id.isin(testids)]
                    estimator=model(config,scenario);estimator.fit(train,train[TARGETS])
                    pred=prediction_rows(test,estimator.predict(test),scenario=scenario,config=name(config),family=config['family'],value=config['value'],fold=fold)
                    # Preserve per-orientation/noise predictions; galaxy controls scoring.
                    records.append(pred)
                record=pd.concat(records,ignore_index=True);record.to_csv(path,index=False)
            group=record.groupby(['subhalo_id','target']).abs_error.mean().reset_index()
            for target,part in group.groupby('target'):
                scores.append(dict(scenario=scenario,target=target,config=name(config),family=config['family'],value=config['value'],MAE=part.abs_error.mean(),n_galaxies=len(part)))
            print('Development CV:',scenario,name(config),flush=True)
    score=pd.DataFrame(scores);score.to_csv(O/'development_CV_scores.csv',index=False)
    joint=score[score.scenario!='optical'].groupby(['target','family','config','value']).MAE.mean().reset_index()
    chosen=joint.sort_values(['MAE','config']).groupby(['target','family'],sort=False).first().reset_index()
    chosen.to_csv(O/'chosen_family_settings.csv',index=False)
    recommended=chosen.sort_values(['MAE','family']).groupby('target',sort=False).first().reset_index()
    recommended.to_csv(O/'recommended_settings.csv',index=False)
    receipt=dict(selection_data='development only; five fixed galaxy folds',
        criterion='Mean galaxy MAE over seeing_NIR and GLAO_NIR developmentCV',
        calibration_partition='validation; not used for feature/hyperparameter selection',
        final_science_opened=False,targets=TARGETS,selected=chosen.to_dict('records'),recommended=recommended.to_dict('records'))
    (O/'MODEL_SELECTION_FROZEN.json').write_text(json.dumps(receipt,indent=2))
    return chosen


def fit_calibrate(chosen=None):
    if chosen is None:chosen=pd.read_csv(O/'chosen_family_settings.csv')
    artifacts=O/'models';artifacts.mkdir(exist_ok=True)
    records=[];thresholds=[]
    for aperture in ['adaptive','fixed12']:
        for scenario in SCENARIOS:
            data=frame(scenario,aperture=aperture,partitions=['development','validation'])
            train=data[(data.partition=='development')&~data.zero_projected_dust]
            validation=data[(data.partition=='validation')&~data.zero_projected_dust]
            controls=data[data.zero_projected_dust]
            for (family,value),requests in chosen.groupby(['family','value']):
                config=dict(family=family,value=int(value));path=artifacts/f'{aperture}_{scenario}_{name(config)}.joblib'
                estimator=model(config,scenario);estimator.fit(train,train[TARGETS]);joblib.dump(estimator,path,compress=3)
                for kind,subset in [('validation',validation),('source_controls',controls)]:
                    if len(subset):
                        pred=prediction_rows(subset,estimator.predict(subset),scenario=scenario,aperture=aperture,condition='nominal',config=name(config),family=family,evaluation=kind)
                        records.append(pred[pred.target.isin(requests.target)])
                if len(validation):
                    residual=abs(estimator.predict(validation)-validation[TARGETS].to_numpy())
                    table=pd.DataFrame(residual,columns=TARGETS);table['subhalo_id']=validation.subhalo_id.to_numpy()
                    maxima=table.groupby('subhalo_id')[TARGETS].max();n=len(maxima);rank=int(np.ceil((n+1)*.8))
                    for target in requests.target:
                        q=float(np.sort(maxima[target])[rank-1]) if rank<=n else np.nan
                        thresholds.append(dict(aperture=aperture,scenario=scenario,family=family,target=target,config=name(config),n_calibration_galaxies=n,rank=rank,halfwidth=q,nominal_coverage=.8))
                print('Fit/calibrated:',aperture,scenario,name(config),flush=True)
    predictions=pd.concat(records,ignore_index=True)
    thresholds=pd.DataFrame(thresholds);thresholds.to_csv(O/'calibration_thresholds.csv',index=False)
    predictions=predictions.merge(thresholds[['aperture','scenario','family','target','halfwidth']],on=['aperture','scenario','family','target'],validate='many_to_one')
    predictions['covered']=predictions.abs_error<=predictions.halfwidth
    predictions.to_csv(O/'validation_and_control_predictions.csv.gz',index=False)
    return predictions


def evaluate_final():
    from freeze_guard import verify
    freeze_hash=verify()
    assert (O/'FINAL_PROTOCOL_FROZEN.json').exists()
    assert not (O/'FINAL_EVALUATION_COMPLETED.json').exists(),'Final evaluation already executed; no rerun/tuning'
    chosen=pd.read_csv(O/'chosen_family_settings.csv');thresholds=pd.read_csv(O/'calibration_thresholds.csv');parts=[]
    for aperture in ['adaptive','fixed12']:
        for scenario in SCENARIOS:
            data=frame(scenario,aperture=aperture,partitions=['final_test'])
            assert data.subhalo_id.nunique()==20
            for (family,value),requests in chosen.groupby(['family','value']):
                config=dict(family=family,value=int(value));estimator=joblib.load(O/'models'/f'{aperture}_{scenario}_{name(config)}.joblib')
                record=prediction_rows(data,estimator.predict(data),scenario=scenario,aperture=aperture,condition='nominal',config=name(config),family=family,evaluation='final_test')
                parts.append(record[record.target.isin(requests.target)])
    final=pd.concat(parts,ignore_index=True)
    final=final.merge(thresholds[['aperture','scenario','family','target','halfwidth']],on=['aperture','scenario','family','target'],validate='many_to_one')
    final['covered']=final.abs_error<=final.halfwidth
    final.to_csv(O/'final_predictions.csv.gz',index=False)
    assert verify()==freeze_hash
    (O/'FINAL_EVALUATION_COMPLETED.json').write_text(json.dumps(dict(galaxies=20,models_retuned=False,final_evaluation_count=1,
        primary_policy='Exclude exact-zero projected-dust galaxies from primary metrics; retain every prediction as separate source controls',
        primary_galaxies=int(final.loc[~final.zero_projected_dust,'subhalo_id'].nunique()),source_control_galaxies=int(final.loc[final.zero_projected_dust,'subhalo_id'].nunique()),
        rows=len(final),freeze_sha256=freeze_hash),indent=2))
    return final


if __name__=='__main__':
    selected=select();fit_calibrate(selected)
