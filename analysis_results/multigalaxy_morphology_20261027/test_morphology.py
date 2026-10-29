import unittest
import numpy as np
from morphology import Geometry, measure
class ScientificChecks(unittest.TestCase):
 def test_gaussian(self):
  g=Geometry(400,.1,12); im=np.exp(-(g.x**2+g.y**2)/8)
  a=measure(im,g)
  self.assertAlmostEqual(a['R50'],2*np.sqrt(2*np.log(2)),delta=.02)
  self.assertAlmostEqual(a['C'],5*np.log10(np.sqrt(np.log(5)/np.log(1.25))),delta=.04)
  self.assertAlmostEqual(a['q'],1,places=8)
  self.assertAlmostEqual(a['A'],0,places=8)
 def test_ellipse_uniform_screen(self):
  g=Geometry(400,.1,12);im=np.exp(-g.x**2/8-g.y**2/2)
  a,b=measure(im,g),measure(im*.37,g)
  for k in ['R50','C','A','q']: self.assertAlmostEqual(a[k],b[k],places=10)
  self.assertAlmostEqual(a['q'],.5,delta=.005)
 def test_signed_and_invalid(self):
  g=Geometry(100,.1,4)
  self.assertTrue(np.isnan(measure(-np.ones((100,100)),g)['R50']))
  im=np.exp(-(g.x**2+g.y**2)); im[g.r>3]=-1e-6
  self.assertLess(measure(im,g)['flux'],np.maximum(im,0)[g.mask].sum())
 def test_offset(self):
  g=Geometry(400,.1,12);im=np.exp(-(g.x**2+g.y**2)/8)
  self.assertGreater(measure(im,Geometry(400,.1,12,.2))['A'],.05)
if __name__=='__main__': unittest.main()
