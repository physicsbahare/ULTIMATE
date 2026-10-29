import unittest
import numpy as np
from audit_sample import valid_pixels
class ProductValidation(unittest.TestCase):
 def test_physical_projection_roundoff(self):
  self.assertTrue(valid_pixels(np.array([[13.,-2.3e-15]]),'stellarage'))
  self.assertFalse(valid_pixels(np.array([[13.,-.1]]),'stellarage'))
  self.assertTrue(valid_pixels(np.array([[1585.,-1.97e-16]]),'stellarmass'))
 def test_broadbands_strict(self):
  self.assertFalse(valid_pixels(np.array([[1.,-1e-15]]),'LSST_g'))
  self.assertFalse(valid_pixels(np.array([[1.,np.nan]]),'LSST_g'))
if __name__=='__main__':unittest.main()
