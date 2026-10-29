"""Check frozen partitions, complete preflight, and inherited offline safety tests."""
import csv,hashlib,importlib.util,json,runpy,sys,unittest
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('/home/bahareh/ULTIMATE');OUT=ROOT/'analysis_results/ml_feasibility_20261027/expansion'
spec=importlib.util.spec_from_file_location('adapter',ROOT/'data/TNG50_SKIRT_DR1_ml_expansion/download_expansion.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
a=adapter.manifest();f=json.loads((OUT/'partitions_frozen.json').read_text())
for name,digest in f['sha256'].items():assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest
rows=list(csv.DictReader((OUT/'galaxy_partitions.csv').open()))
assert len(rows)==len({r['subhalo_id'] for r in rows})==120
assert Counter(r['partition'] for r in rows)=={'development':86,'validation':14,'final_test':20}
assert all(r['partition']=='development' for r in rows if r['provenance']=='existing')
assert sum(r['provenance']=='existing' for r in rows)==26
pre=json.loads((adapter.d.OUT/'preflight.json').read_text())
probes=[r for r in pre['probes'] if r['probe']=='archive_range_size']
assert len(probes)==94 and {r['subhalo_id'] for r in probes}=={r['subhalo_id'] for r in a['selected']}
assert a['expected_total_bytes']==sum(r['expected_bytes'] for r in probes)<adapter.d.CAP
assert all(r['status']==206 and r['bytes_read']==1024 for r in probes)
sys.modules['download_dr1']=adapter.d
ns=runpy.run_path(str(ROOT/'data/TNG50_SKIRT_DR1_extra/test_downloader.py'))
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ns['Tests']))
assert result.wasSuccessful()
print('PASS:120 unique frozen IDs,86/14/20 partitions,94 complete preflight size/range checks, six inherited security/integrity/resume tests with expansion configuration.')
