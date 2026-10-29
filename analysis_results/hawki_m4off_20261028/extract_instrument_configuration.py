from pathlib import Path
from astropy.io import fits
import pandas as pd
O=Path(__file__).resolve().parent;rows=[]
for p in sorted((O.parents[1]/'data/HAWKI_M4off_2019').glob('*.fits')):
 with fits.open(p) as h:
  for k,v in h[0].header.items():
   if k.startswith(('ESO DET','ESO AOS','ESO INS MODE','ESO INS FILT','ESO INS AO OPTI','ESO ADA ABSROT','ESO TEL AIRM')):
    rows.append(dict(product=p.name,key=k,value=str(v),comment=h[0].header.comments[k],scope='inherited primary header snapshot, not per-exposure telemetry'))
pd.DataFrame(rows).to_csv(O/'instrument_configuration.csv',index=False)
print('Saved instrument/header snapshots',len(rows))
