from model_study import *

def run():
 settings=json.loads((O/'model_settings.json').read_text());rows=[]
 for tag,cfg in settings.items():
  if cfg['model']=='constant':continue
  model=joblib.load(O/'models'/f'{tag}.joblib')[-1]
  values=model.coef_ if cfg['model']=='ridge' else model.feature_importances_
  for c,v in zip(cfg['features'],values):rows.append(dict(tag=tag,model=cfg['model'],feature=c,value=float(v),definition='target change per training-feature SD, conditional/correlated' if cfg['model']=='ridge' else 'training impurity importance; not validation or causal importance'))
 pd.DataFrame(rows).to_csv(O/'model_feature_interpretation.csv',index=False);print('Model coefficient/importance records saved; no feature selection')
if __name__=='__main__':run()
