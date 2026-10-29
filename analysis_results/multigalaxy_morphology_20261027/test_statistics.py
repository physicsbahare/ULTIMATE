"""Scientific regression: missing moments cannot change the strategy comparison sample."""
import unittest
import numpy as np,pandas as pd
from statistics_analysis import score_observations,interval
class PairedScoreTests(unittest.TestCase):
 def data(self):
  rows=[]
  for mode in ['seeing','glao']:
   for phase in ['reference','psf','noise']:
    for scene in ['clear','dusty']:
     for pairing in (['common','independent_clear'] if scene=='clear' and phase=='noise' else ['common']):
      x=1. if scene=='clear' else 1.1
      row=dict(subhalo_id=1,view='O1',band='2MASS_Ks',z=.1,hours=1.,kind='gaussian',mode=mode,phase=phase,scene=scene,pairing=pairing,draw=0 if phase=='noise' else -1,flux=1.,R50=x,C=x,A=x,A_raw=x,q=x)
      if mode=='seeing' and phase=='noise' and scene=='clear':row['q']=np.nan
      rows.append(row)
  return pd.DataFrame(rows)
 def test_joint_missing_strategy_draw(self):
  s,_=score_observations(self.data());q=s[s.metric=='q']
  self.assertTrue(q.dust_delta_abs_error.isna().all())
  self.assertTrue(q.preservation_abs_error.notna().all())
  self.assertTrue(s[s.metric=='R50'].dust_delta_abs_error.eq(0).all())
 def test_degenerate_bootstrap(self):
  np.testing.assert_array_equal(interval(np.ones(26)),[1.,1.])
if __name__=='__main__':unittest.main()
