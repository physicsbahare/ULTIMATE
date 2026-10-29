"""Analytic numerical checks for the new-width wrapper, no science execution."""
import unittest
import numpy as np
import run_assessment as a

class OperatorTests(unittest.TestCase):
    def test_moffat_width_is_fwhm_not_d50(self):
        alpha,d50=a.width_parameters(.2,'moffat')
        self.assertAlmostEqual((1+(.1/alpha)**2)**(-a.BETA),.5,places=12)
        self.assertGreater(d50,.2)
        self.assertAlmostEqual(1-(1+(d50/2/alpha)**2)**(1-a.BETA),.5,places=12)
    def test_kernel_positive_and_normalized(self):
        for family in ['gaussian','moffat']:
            k=a.kernel(.2,.0542,family,2)
            self.assertTrue(np.all(k>=0))
            self.assertAlmostEqual(k.sum(),1.,places=13)
    def test_two_pixel_psf_integrates_for_detector_phases(self):
        for family in ['gaussian','moffat']:
            for phase in [0.,.05]:
                row=a.point_check(.2,family,.0542,phase)
                self.assertLess(row['relative_L1_analytic'],.02)
                self.assertLess(abs(row['detector_flux']-1),1e-4)
    def test_fold_keeps_whole_galaxies(self):
        folds=a.make_folds(list(range(13)))
        self.assertEqual(len(folds),13)
        self.assertEqual(folds.subhalo_id.nunique(),13)
        self.assertEqual(set(folds.fold),set(range(5)))

if __name__=='__main__':unittest.main()
