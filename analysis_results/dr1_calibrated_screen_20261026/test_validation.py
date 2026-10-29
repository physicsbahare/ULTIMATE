"""Independent numerical checks for physics, inference and calibration."""
import unittest
import numpy as np
from scipy.stats import beta
import experiment as e
class Validation(unittest.TestCase):
 def test_law_normalization(self):
  for n in [.7,1,1.3]: self.assertAlmostEqual(float(e.kappa(.44,n)-e.kappa(.55,n)),1)
 def test_flux_transfer(self):
  a=np.ones((10,10)); v=e.overlap_flux(a,np.arange(11),np.linspace(0,10,18)); self.assertAlmostEqual(v.sum(),100)
  self.assertAlmostEqual(float(e.specific_intensity_transfer(1.,.3)),1/1.3**3)
 def test_electron_moments(self):
  r=np.random.default_rng(443); s=np.full(80000,4.); x,v=e.draw_exposures(s,100,.01,30,4,16,r)
  self.assertLess(abs(x.mean()-480),2); self.assertLess(abs(x.var()/v[0]-1),.025)
 def test_contrast_and_likelihood(self):
  h=e.contrasts(5);np.testing.assert_allclose(h@np.ones(5),0,atol=1e-14);np.testing.assert_allclose(h@h.T,np.eye(4),atol=1e-14)
  n=np.eye(6);k=np.eye(6)*2; a=e.GaussianModel(n,k);x=np.arange(6.)[None,:]
  self.assertAlmostEqual(a.logpdf(x)[0],-.5*(np.sum(x*x)/3+6*np.log(3)))
 def test_independent_seeds_and_ci(self):
  self.assertNotEqual(e.seed_for(1,0),e.seed_for(1,1));lo,hi=e.binomial_ci(0,200);self.assertEqual(lo,0);self.assertGreater(hi,0.01)
 def test_calibration_order_statistic(self):
  # Independent null test: known distribution, no astronomy/template oracle.
  r=np.random.default_rng(121);c=r.normal(size=2000);t=e.threshold(c);rate=np.mean(r.normal(size=100000)>t);self.assertLess(abs(rate-.05),.02)
 def test_no_truth_means_in_inference(self):
  r=np.random.default_rng(177);draw=100+r.normal(size=(20,2,15));c=np.tile(np.eye(15),(2,1,1))
  y,n,h=e.prepare_data(draw,np.zeros((2,15)),c,[0,1]);yy,nn,_=e.prepare_data(draw,np.full((2,15),1e20),c,[0,1])
  np.testing.assert_array_equal(y,yy);np.testing.assert_array_equal(n,nn)
 def test_signed_linear_projection(self):
  g=e.geometry(.3,'glao','native');q=np.ones((7,400,400));a,_=e.render(q,.3,g);b,_=e.render(-.2*q,.3,g,signed=True);c,_=e.render(.8*q,.3,g)
  np.testing.assert_allclose(a+b,c,rtol=1e-11,atol=1e-10)
 def test_posterior_predictive_discrepancy(self):
  # With zero latent uncertainty, the discrepancy has the ordinary noise law.
  m=e.GaussianModel(np.eye(12),np.zeros((12,12)));y=np.ones(12)
  p,q,rep=e.posterior_check(m,y);self.assertLess(abs(p-float(__import__('scipy').stats.chi2.sf(12,12))),.06)
 def test_population_ensemble_positive_and_independent(self):
  import final_ensemble as f
  a=f.coefficients(500,0).reshape(500,2,6);b=f.coefficients(500,1).reshape(500,2,6)
  self.assertLessEqual(float(np.sum(abs(a),axis=2).max()),1.);self.assertFalse(np.array_equal(a,b))
if __name__=='__main__': unittest.main()
