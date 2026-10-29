from pathlib import Path
import time
import pandas as pd
from model_study import S,run
meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');ids=meta[meta.partition!='final_test'].subhalo_id
while True:
 n=sum((S/'derived'/str(s)/'complete.json').exists() for s in ids)
 print('Complete nonfinal feature products',n,'/100',flush=True)
 if n==100:break
 time.sleep(30)
run()
