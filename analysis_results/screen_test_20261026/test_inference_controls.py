import unittest
import numpy as np
from screen_inference import fit_screen_models
class InferenceControls(unittest.TestCase):
 def test_uniform_shapes_prefer_uniform(self):
  av=np.linspace(0,2,21); lam=np.array([.4,.55,.8,1.2,2.])
  shape=10**(-.4*av[:,None]*(lam[None,:]/.55)**-1)
  amps=np.linspace(1,3,20)
  flux=amps[:,None]*shape[7][None,:]
  variance=np.full_like(flux,.01**2)
  result=fit_screen_models(flux,variance,shape,1,len(av),1)
  self.assertLess(result['log_B_variable_uniform'],-10)
 def test_variable_shapes_prefer_variable(self):
  av=np.linspace(0,2,21); lam=np.array([.4,.55,.8,1.2,2.])
  shape=10**(-.4*av[:,None]*(lam[None,:]/.55)**-1)
  flux=np.linspace(1,3,20)[:,None]*shape[np.arange(20)]
  variance=np.full_like(flux,.01**2)
  result=fit_screen_models(flux,variance,shape,1,len(av),1)
  self.assertGreater(result['log_B_variable_uniform'],100)
if __name__=='__main__':unittest.main()
