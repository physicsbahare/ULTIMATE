#!/home/bahareh/miniforge3/envs/phd/bin/python
"""Configure the established secure DR1 downloader for the frozen94 sample.

Archive integrity reads bytes only: no FITS parsing or image analysis occurs.
"""
import importlib.util,json,hashlib,sys,re
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('/home/bahareh/ULTIMATE')
spec=importlib.util.spec_from_file_location('secure_dr1',ROOT/'data/TNG50_SKIRT_DR1_extra/download_dr1.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
d.OUT=Path(__file__).resolve().parent
d.PIDFILE=d.OUT/'download.pid'
# All94 must fit within this compressed archive cap, while every chunk also
# enforces the established100GiB free reserve +256MiB safety headroom.
d.CAP=100*2**30
_log=d.log
def log(message):
    _log(re.sub(r'(?<![.\d])65 GiB','100 GiB',message).replace('25 archives','94 archives').replace('/25 verified','/94 verified'))
d.log=log
def manifest():
    a=json.loads((d.OUT/'selection_manifest.json').read_text());ids=[int(x['subhalo_id']) for x in a['selected']]
    frozen_path=ROOT/'analysis_results/ml_feasibility_20261027/expansion/partitions_frozen.json'
    if hashlib.sha256(frozen_path.read_bytes()).hexdigest()!=a['partition_freeze_sha256']:raise d.SafeFailure('Frozen partition hash mismatch')
    f=json.loads(frozen_path.read_text())
    if len(ids)!=94 or len(set(ids))!=94 or set(ids)&set(a['excluded_ids']):raise d.SafeFailure('Invalid94-object selection or duplicate')
    if {k:len(v) for k,v in f['partitions'].items()}!={'development':86,'validation':14,'final_test':20}:raise d.SafeFailure('Invalid frozen partition counts')
    if set(ids)!={sid for part in f['partitions'].values() for sid in part if sid not in a['excluded_ids']}:raise d.SafeFailure('Selection differs from frozen partition IDs')
    if sum(int(x.get('expected_bytes',0)) for x in a['selected'])>d.CAP:raise d.Pause('Preflight archive total exceeds100GiB budget')
    return a
d.manifest=manifest
if __name__=='__main__':
    try:
        if '--preflight' in sys.argv:d.preflight()
        else:d.run()
    except Exception as exc:
        d.log('Stopped: '+(str(exc) if isinstance(exc,d.SafeFailure) else type(exc).__name__));sys.exit(1)
