import unittest
import numpy as np
class PhysicsTests(unittest.TestCase):
 def test_transfer_and_flux(self):
  from forward_physics import overlap_flux,cosmology,specific_intensity_transfer
  a=np.arange(25,dtype=float).reshape(5,5)
  edges=np.linspace(-2.5,2.5,14)
  b=overlap_flux(a,np.arange(6)-2.5,edges)
  self.assertAlmostEqual(b.sum(),a.sum(),places=10)
  self.assertTrue(np.allclose(overlap_flux(a,np.arange(6)-2.5,np.arange(6)-2.5),a))
  for z in [.1,.3,1.,3.]:
   da=cosmology.angular_diameter_distance(z).value; dl=cosmology.luminosity_distance(z).value
   self.assertAlmostEqual(dl/da,(1+z)**2,places=10)
   self.assertAlmostEqual(specific_intensity_transfer(1.,z),(1+z)**-3)
 def test_flat_spectrum_electrons(self):
  from forward_physics import photon_rate_jy
  h=6.62607015e-34; area=50.; lo=1.; hi=2.
  expected=1e-26*area/h*np.log(hi/lo)*.4
  actual=photon_rate_jy(np.ones(10001),np.linspace(lo,hi,10001),np.full(10001,.4),area)
  self.assertLess(abs(actual/expected-1),1e-7)
 def test_no_spectral_extrapolation(self):
  from forward_physics import interpolate_sed
  with self.assertRaises(ValueError): interpolate_sed(np.array([1.,2.]),np.array([1.,2.]),np.array([.8]))
 def test_split_noise(self):
  from forward_physics import draw_exposures
  src=np.full((500,500),2.); bg=10.; dark=.1; rn=4.
  y,var=draw_exposures(src,bg,dark,20.,4,rn,np.random.default_rng(500))
  expected_var=(2+10+.1)*80+4*rn**2
  self.assertLess(abs(y.mean()-160),.3)
  self.assertLess(abs(y.var()/expected_var-1),.015)
  self.assertTrue(np.allclose(var,expected_var))
 def test_evidence_identity(self):
  from screen_inference import hierarchical_screen_evidence
  # Constant likelihood in Av: the global and local hypotheses have identical normalized evidence.
  ll=np.full((3,7,5),-2.)
  u,v=hierarchical_screen_evidence(ll)
  self.assertAlmostEqual(u,v,places=10)
  self.assertAlmostEqual(u,-14.,places=10)
if __name__=='__main__': unittest.main()
