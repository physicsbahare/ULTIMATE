"""Deterministic staged entrypoint. Restart skips verified completed measurements."""
import audit_sample,observe,validate_science,statistics_analysis
from pathlib import Path
O=Path(__file__).resolve().parent

def run():
 dev=[294866,167418,626287,535051,638950]
 audit_sample.run(dev)
 observe.run(dev)
 validate_science.gate()
 audit_sample.run()
 observe.run(sensitivity=True)
 statistics_analysis.run()
 import additional_robustness
 additional_robustness.run()
 import null_diagnostics
 null_diagnostics.run()
 import presentation
 presentation.run()
if __name__=='__main__':run()
