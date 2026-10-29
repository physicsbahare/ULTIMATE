"""Reproduce only this focused analysis, never the old full grid."""
import os,sys
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl');sys.dont_write_bytecode=True
if __name__=='__main__':
 import diagnose,diagnose_transforms,physical_model,develop,pilot,native_adequacy,information,degeneracy,degeneracy_bound,aperture_information,absolute_failure,compare_gaussian,existing_band_check,make_report
 diagnose.run();diagnose_transforms.run();physical_model.train_templates();develop.run()
 # Failed raw gate leads only to the explicitly bounded diagnostic pilot.
 pilot.run();native_adequacy.run();information.run();degeneracy.run();degeneracy_bound.run();aperture_information.run();absolute_failure.run();compare_gaussian.run();existing_band_check.run();make_report.run()
