"""Development-only tuning, sealed final20; all uncertainty units are galaxies."""
from pathlib import Path
import json,hashlib,sys,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl')
import numpy as np,pandas as pd,joblib
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error
O=Path(__file__).resolve().parent;S=O.parent/'ml_expanded_20261028';SEED=20261028
TARGETS=['A_g','dR50_Ks','dC_Ks','A_Ks','A_g_p50_1kpc','A_g_IQR_1kpc']

def feature_cols(columns,bandset,kind):
 bands=['g'] if bandset=='optical' else ['g','J','Ks']
 photo=[b+'_logJy' for b in bands]+([] if len(bands)==1 else ['color_g_J','color_J_Ks'])
 if kind=='photo':return photo
 cols=photo.copy()
 for b in bands:
  cols += [b+'_'+x for x in ['R50','C','A','q','radial0','radial1','radial2','radial3','harmonic1','harmonic2','harmonic4']]
  if b in ['g','Ks']:cols += [b+'_texture_'+x for x in ['0.5','1.0','2.0']]
 if len(bands)>1:cols+=['gradient_g_J','gradient_J_Ks']
 if kind=='spatial':cols += [c for c in columns if any(c.startswith('cell_'+b+'_') for b in bands)]
 return list(dict.fromkeys(cols))

def estimator(name,setting):
 if name=='ridge':m=Ridge(alpha=setting)
 elif name=='forest':m=RandomForestRegressor(n_estimators=120,min_samples_leaf=setting,max_features=.75,n_jobs=2,random_state=SEED)
 else:m=GradientBoostingRegressor(n_estimators=100,max_depth=2,min_samples_leaf=setting,learning_rate=.04,loss='huber',random_state=SEED)
 return make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),StandardScaler(),m)

def group_mae(y,p,groups):return pd.DataFrame({'g':groups,'e':abs(y-p)}).groupby('g').e.mean().mean()

def choose(X,y,groups,name):
 options={'ridge':[1.,10.,100.,1000.],'forest':[8,24],'boost':[12,32]}[name]
 folds=list(GroupKFold(5).split(X,y,groups));rows=[]
 for v in options:
  pred=np.zeros(len(y))
  for tr,te in folds:pred[te]=estimator(name,v).fit(X.iloc[tr],y[tr]).predict(X.iloc[te])
  rows.append((group_mae(y,pred,groups),v))
 score,setting=min(rows);return setting,score,rows

def metrics(pred,keys):
 records=[]
 for key,p in pred.groupby(keys,dropna=False):
  d=p.assign(ae=abs(p.truth-p.prediction),se=(p.truth-p.prediction)**2,b=p.prediction-p.truth)
  galaxy=d.groupby('subhalo_id')[['ae','se','b']].mean();rng=np.random.default_rng(SEED)
  boot=galaxy.ae.to_numpy()[rng.integers(len(galaxy),size=(2000,len(galaxy)))].mean(axis=1)
  records.append(dict(zip(keys,key if isinstance(key,tuple) else (key,)),MAE=galaxy.ae.mean(),RMSE=np.sqrt(galaxy.se.mean()),bias=galaxy.b.mean(),MAE_lo=np.quantile(boot,.025),MAE_hi=np.quantile(boot,.975),n_galaxies=len(galaxy)))
 return pd.DataFrame(records)

def load_snapshot():
 meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');allow=meta[meta.partition!='final_test']
 finals=set(meta[meta.partition=='final_test'].subhalo_id);paths=[S/'derived'/str(s) for s in allow.subhalo_id]
 assert all((p/'complete.json').exists() for p in paths),'Wait for all100 nonfinal feature products'
 val=meta[meta.partition=='validation'].subhalo_id.to_numpy(copy=True);np.random.default_rng(SEED).shuffle(val)
 split={'calibration':[int(x) for x in val[:7]],'assessment':[int(x) for x in val[7:]],'final_science_opened':False}
 (O/'validation_interval_split.json').write_text(json.dumps(split,indent=2))
 hashes={};fs=[];ys=[]
 for p in paths:
  for file in ['features.csv.gz','labels.csv']:
   f=p/file;hashes[str(f.relative_to(S.parent))]=hashlib.sha256(f.read_bytes()).hexdigest()
  fs.append(pd.read_csv(p/'features.csv.gz'));ys.append(pd.read_csv(p/'labels.csv'))
 f=pd.concat(fs,ignore_index=True);y=pd.concat(ys,ignore_index=True)
 assert not set(f.subhalo_id)&finals and not set(y.subhalo_id)&finals
 assert not f.duplicated(['subhalo_id','view','aperture','condition','mode','draw']).any()
 assert not y.duplicated(['subhalo_id','view','aperture']).any()
 assert f.groupby('subhalo_id').view.nunique().eq(5).all()
 f.to_csv(O/'feature_table.csv.gz',index=False);y.to_csv(O/'target_table.csv',index=False)
 (O/'input_hashes.json').write_text(json.dumps(hashes,indent=2))
 return meta,f,y,split

def run():
 meta,f,y,split=load_snapshot();allpred=[];tuning=[];learning=[];ood=[];cal=[];settings={}
 configs=[('constant','photo','median'),('constant','photo','mean'),('ridge','photo',None),('ridge','summary',None),('forest','summary',None),('boost','summary',None),('ridge','spatial',None)]
 for ap in ['fixed12','adaptive']:
  for bands,mode in [('optical','seeing'),('nir','seeing'),('nir','glao')]:
   data=f[(f.aperture==ap)&(f.condition=='nominal')&(f['mode']==mode)].merge(y[y.aperture==ap],on=['subhalo_id','view','partition','aperture'],validate='many_to_one')
   train=data[(data.partition=='development')&(~data.zero_projected_dust)].reset_index(drop=True)
   test=data[data.partition=='validation'].copy();control=data[(data.partition=='development')&data.zero_projected_dust].copy()
   for target in TARGETS:
    for name,kind,fix in configs:
     tag='_'.join([ap,bands,mode,target,name,kind,str(fix or '')]);cols=feature_cols(f.columns,bands,kind)
     assert all(c in f.columns for c in cols);X=train[cols];yy=train[target].to_numpy();groups=train.subhalo_id.to_numpy()
     if name=='constant':setting=fix;score=np.nan;m=None;value=getattr(np,fix)(yy)
     else:
      setting,score,grid=choose(X,yy,groups,name);m=estimator(name,setting).fit(X,yy)
      tuning.extend([dict(tag=tag,setting=v,development_CV_MAE=sc) for sc,v in grid]);joblib.dump(m,O/'models'/f'{tag}.joblib')
     settings[tag]={'features':cols,'model':name,'setting':setting,'development_CV_MAE':score,'constant':float(value) if name=='constant' else None}
     for stage,t in [('validation',test),('source_controls',control)]:
      if len(t)==0:continue
      p=t[['subhalo_id','view','draw','zero_projected_dust','log_stellar_mass','SFR_Msun_yr','dust_mass_field_Msun','radius_kpc','Ks_q','g_q','Ks_logJy','reference_aperture_limited']].copy()
      p['truth']=t[target].to_numpy();p['prediction']=value if m is None else m.predict(t[cols]);p['target']=target;p['aperture']=ap;p['bands']=bands;p['mode']=mode;p['model']=name+'_'+kind+(('_'+fix) if fix else '');p['stage']=stage;p['tag']=tag
      if target.startswith('d'):
       metric=target[1:].replace('_Ks','');p['clear_native']=t['clear_'+metric+'_Ks'].to_numpy();p['dusty_native']=t['dusty_'+metric+'_Ks'].to_numpy();p['observed']=t['Ks_'+metric].to_numpy();p['corrected']=p.observed-p.prediction
       p['native_corrected']=p.dusty_native-p.prediction
      allpred.append(p)
      if stage=='validation':
       scores=p[p.subhalo_id.isin(split['calibration'])].assign(res=lambda x:abs(x.truth-x.prediction)).groupby('subhalo_id').res.max();assert len(scores)==7
       width=float(np.sort(scores)[int(np.ceil(8*.8))-1]);ass=p[p.subhalo_id.isin(split['assessment'])].copy();ass['covered']=abs(ass.truth-ass.prediction)<=width
       cal.append(dict(tag=tag,half_width=width,calibration_galaxies=7,assessment_galaxies=7,entire_galaxy_coverage=ass.groupby('subhalo_id').covered.all().mean(),row_coverage=ass.covered.mean()))
     # Learning and OOD use fixed12 NIR for predeclared interpretable ridge models.
     if ap=='fixed12' and bands=='nir' and name=='ridge' and kind in ['photo','spatial'] and target in TARGETS[:3]:
      for fold,(tr,te) in enumerate(GroupKFold(5).split(X,yy,groups)):
       ids=np.unique(groups[tr]);np.random.default_rng(SEED+fold).shuffle(ids)
       for n in sorted(set([12,24,48,len(ids)])):
        if n>len(ids):continue
        ix=tr[np.isin(groups[tr],ids[:n])];local_setting,_,_=choose(X.iloc[ix].reset_index(drop=True),yy[ix],groups[ix],name);pred=estimator(name,local_setting).fit(X.iloc[ix],yy[ix]).predict(X.iloc[te]);learning.append(dict(tag=tag,fold=fold,n_train_galaxies=n,MAE=group_mae(yy[te],pred,groups[te]),settings_selected_with_all_development=False))
      mass=train.groupby('subhalo_id').log_stellar_mass.mean();hi=mass[mass>=mass.quantile(.75)].index;tr=~train.subhalo_id.isin(hi);te=~tr
      # Retune strictly on low-mass training galaxies.
      st,_,_=choose(X[tr].reset_index(drop=True),yy[tr],groups[tr],name);pred=estimator(name,st).fit(X[tr],yy[tr]).predict(X[te])
      base=train[tr].groupby('subhalo_id')[target].mean().median();ood.append(dict(tag=tag,n_train=len(set(groups[tr])),n_test=len(hi),MAE=group_mae(yy[te],pred,groups[te]),constant_MAE=group_mae(yy[te],np.full(te.sum(),base),groups[te]),setting=st))
    print(ap,bands,mode,target,flush=True)
  # checkpoint
  pd.concat(allpred,ignore_index=True).to_csv(O/'heldout_predictions.csv.gz',index=False)
 pred=pd.concat(allpred,ignore_index=True);keys=['stage','aperture','bands','mode','target','model','tag']
 metrics(pred,keys).to_csv(O/'model_comparison.csv',index=False)
 pred.assign(ae=abs(pred.truth-pred.prediction)).groupby(keys+['subhalo_id']).ae.mean().reset_index().to_csv(O/'galaxy_residuals.csv',index=False)
 pd.DataFrame(tuning).to_csv(O/'development_tuning.csv',index=False);pd.DataFrame(cal).to_csv(O/'uncertainty_calibration.csv',index=False);pd.DataFrame(learning).to_csv(O/'learning_curves.csv',index=False);pd.DataFrame(ood).to_csv(O/'OOD_summary.csv',index=False)
 (O/'model_settings.json').write_text(json.dumps(settings,indent=2));(O/'execution_complete.json').write_text(json.dumps({'nonfinal_galaxies':100,'final_science_opened':False,'models':len(settings),'sklearn':__import__('sklearn').__version__},indent=2))
 return pred
if __name__=='__main__':run()
