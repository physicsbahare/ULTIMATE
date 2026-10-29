"""Independent analytic/radiometric checks and original-pilot reconciliation."""
from pathlib import Path
import json,unittest
import numpy as np,pandas as pd
import observe as ob
from morphology import measure
O=Path(__file__).resolve().parent;p=ob.p

def run():
 import test_morphology
 result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(test_morphology));assert result.wasSuccessful()
 c,d,_=ob.load(294866,'O1');oc,od,_=p.load('O1');assert np.array_equal(c,oc) and np.array_equal(d,od)
 g=p.make_geometry(.1,'glao');mg=ob.geometry(g);rr,loss=p.render(d,g);assert loss<1e-8
 rows=[]
 for j,b in enumerate(ob.BANDS):
  m=measure(rr[j],mg);old=p.morph(rr[j],np.zeros(g['shape']),g)
  for k,ok in [('R50','R50'),('C','C'),('A','A'),('q','axis_ratio')]:
   e=abs(m[k]-old[ok]);assert e<1e-10;rows.append(dict(test='pilot_morphology_reproduction',band=b,metric=k,error=e))
 # Prior published dust-minus-clear reference, draw=-1 (no observational PSF).
 saved=pd.read_csv(O.parent/'spatial_structure_pilot_20261026/dust_morphology_paired_draws.csv');saved=saved[(saved.view=='O1')&(saved.z==.1)&(saved['mode']=='glao')&(saved.hours==1)&(saved.kind=='gaussian')&(saved.draw==-1)]
 rc,_=p.render(c,g,False);rd,_=p.render(d,g,False)
 for j,b in [(0,'g'),(2,'Ks')]:
  a,bb=measure(rd[j],mg),measure(rc[j],mg);s=saved[saved.band==b].iloc[0]
  for k,ok in [('R50','R50'),('C','C'),('A','A'),('q','axis_ratio')]:
   e=abs(a[k]-bb[k]-s[ok]);assert e<1e-10;rows.append(dict(test='published_paired_reference',band=b,metric=k,error=e))
 # Exact aggregate Poisson plus summed reads reproduces declared split-exposure variance.
 rng=np.random.default_rng(9134);noise=[]
 for j,b in enumerate(p.INST):
  src=float(np.median(rr[j][g['roi']]));t=3600.;bg=b['background_e_s_pixel']+b['dark_e_s'];n=60
  exact=(rng.poisson((src+bg)*t,100000)-(src+bg)*t+rng.normal(0,np.sqrt(n)*b['read_noise_e'],100000))/t
  declared=((src+bg)*t+n*b['read_noise_e']**2)/t**2
  ratio=np.var(exact,ddof=1)/declared;mean_z=np.mean(exact)/np.sqrt(declared/len(exact));assert abs(ratio-1)<.025 and abs(mean_z)<4
  noise.append(dict(band=ob.BANDS[j],empirical_declared_variance_ratio=ratio,mean_z=mean_z,poisson_count_mean=(src+bg)*t,source=src,background=bg,reads=n))
 # Independent area integration of a constant image: total flux invariant on enclosing grid.
 edges=np.linspace(-2,2,81);outs=np.linspace(-2.1,2.1,29);image=np.ones((80,80));out=p.overlap_flux(image,edges,outs)
 fluxerr=abs(out.sum()/image.sum()-1);assert fluxerr<1e-12
 pd.DataFrame(rows).to_csv(O/'benchmark_reproduction.csv',index=False);pd.DataFrame(noise).to_csv(O/'noise_validation.csv',index=False)
 checks=dict(analytic_tests_passed=result.testsRun,pilot_cache_bitwise_equal=True,published_morphology_max_error=max(x['error'] for x in rows),gaussian_padded_flux_loss=loss,overlap_flux_relative_error=fluxerr,aggregate_Poisson_split_read_moments_passed=True)
 (O/'numerical_validation.json').write_text(json.dumps(checks,indent=2));print(checks)
 return checks

def gate():
 checks=run();ids=[294866,167418,626287,535051,638950]
 records=[]
 for sid in ids:
  rec=json.loads((O/'cache'/str(sid)/'complete.json').read_text());assert rec['complete_pairing'] and rec['current_gzip_CRC']=='passed'
  a=pd.read_csv(O/'cache'/str(sid)/'intrinsic.csv');assert np.isfinite(a[['R50','C','A','q']]).all().all()
  for view in [f'O{i}' for i in range(1,6)]:
   f=pd.read_csv(O/'cache'/str(sid)/f'{view}_observed.csv');assert np.isfinite(f[['R50','C','A']]).all().all()
   assert np.isfinite(f.loc[f.phase!='noise','q']).all()
   tr=pd.read_csv(O/'cache'/str(sid)/f'{view}_transfer.csv');assert tr.padded_flux_loss.max()<1e-6
  obs=pd.concat([pd.read_csv(O/'cache'/str(sid)/f'{v}_observed.csv') for v in [f'O{i}' for i in range(1,6)]])
  records.append(dict(subhalo_id=sid,intrinsic_rows=len(a),noisy_q_failures=int(obs.q.isna().sum()),passed=True))
 checks.update(passed=True,development_galaxies=records,remaining_evaluation_galaxies=21,protocol_sha256=__import__('hashlib').sha256((O/'PROTOCOL.md').read_bytes()).hexdigest())
 dest=O/'development_gate.json'
 if dest.exists():
  saved=json.loads(dest.read_text());assert saved['passed'] and saved['protocol_sha256']==checks['protocol_sha256']
  (O/'development_gate_recheck.json').write_text(json.dumps(checks,indent=2))
 else:dest.write_text(json.dumps(checks,indent=2))
 print('DEVELOPMENT GATE PASSED')
if __name__=='__main__':
 import sys
 gate() if '--gate' in sys.argv else run()
