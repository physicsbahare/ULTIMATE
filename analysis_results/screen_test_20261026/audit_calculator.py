from pathlib import Path
import os,runpy,builtins,json
import numpy as np
O=Path(__file__).resolve().parent; C=O/'sources/calculator/sensitivity'
os.chdir(C)
old=builtins.input; builtins.input=lambda prompt='':''
ns=runpy.run_path(str(C/'ultimate.py')); builtins.input=old
rows=[]
for band,lam,width,trans in zip(ns['filter_info'][0],ns['filter_info'][1],ns['filter_info'][2],ns['filter_info'][3]):
 fsky=.58 if 1.4<lam<1.8 else 1.
 b=ns['bgcalc'](lam,width,fsky,273.,trans,.45)
 rows.append({'band':band,'lambda_um':lam,'width_um':width,'filter_peak':trans,'sky_e_s_arcsec2_published':b[1],'telescope_e_s_arcsec2_published':b[2],'moon_e_s_arcsec2_published':b[3],'telescope_throughput':b[4],'atmosphere_mean':b[5],'instrument_without_filter':b[6],'AB15_e_s_published':ns['f0'](15,b[5],b[4],b[6],trans,lam,width)})
(O/'calculator_exact_components.json').write_text(json.dumps(rows,indent=2))
ns['lm'].to_csv(O/'calculator_original_1h_output.csv',index=False)
print(json.dumps(rows,indent=2))
