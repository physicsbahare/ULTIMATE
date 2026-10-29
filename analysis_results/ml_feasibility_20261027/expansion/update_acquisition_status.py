"""Refresh a safe timestamped acquisition snapshot; never opens archive contents."""
import json,os,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('/home/bahareh/ULTIMATE');OUT=Path(__file__).resolve().parent;DATA=ROOT/'data/TNG50_SKIRT_DR1_ml_expansion'
a=json.loads((DATA/'selection_manifest.json').read_text())
state=json.loads((DATA/'download_state.json').read_text()) if (DATA/'download_state.json').exists() else {}
pid=state.get('pid');alive=False
if pid:
    try:os.kill(pid,0);alive=True
    except ProcessLookupError:alive=False
    except PermissionError:alive='permission denied to process probe'
verified=[int(sid) for sid,r in state.get('galaxies',{}).items() if r.get('status')=='verified']
parts=[{'name':p.name,'bytes':p.stat().st_size} for p in DATA.glob('*.tar.gz.part')]
s={'observed_utc':datetime.now(timezone.utc).isoformat(),'new_selected':94,'new_verified':len(verified),'new_verified_ids':verified,'existing_previously_verified':26,'combined_verified_total':26+len(verified),'expected_total_bytes':a['expected_total_bytes'],'expected_total_GiB':a['expected_total_bytes']/2**30,'batch_pid':pid,'pid_alive':alive,'batch_status':state.get('status','not_started'),'current':state.get('current'),'partials':parts,'compressed_bytes_present':sum(p.stat().st_size for p in DATA.glob('*.tar.gz*')),'free_GiB':shutil.disk_usage(DATA).free/2**30,'final_test_scientific_images_opened':0,'blocker':None if alive is True else 'Downloader is not confirmed live; inspect state and restart launcher if appropriate.','note':'Detached resumable batch. CRC/tar-byte integrity validation does not inspect FITS image values. This is a timestamped snapshot; inspect live state for updates.'}
(OUT/'acquisition_status.json').write_text(json.dumps(s,indent=2)+'\n')
report=f'''# DR1 expansion acquisition status

Observed {s['observed_utc']}. The galaxy split is frozen at86 development,14 validation and20 untouched final-test galaxies. The exact IDs and official metadata are in `galaxy_partitions.csv`; reproducibility, selection probabilities, limits and monitoring commands are in `README.md`.

All94 new archives passed authenticated gzip/range/size preflight: **{s['expected_total_bytes']:,} bytes ({s['expected_total_GiB']:.3f}GiB)**. The batch PID is **{pid}**, live-process probe **{alive}**, batch status **{s['batch_status']}**. **{s['new_verified']}/94 new archives** have completed full gzip CRC/tar-byte/SHA256 verification; with26 existing archives, **{s['combined_verified_total']}/120 total** are verified at this observation. Compressed bytes currently present: **{s['compressed_bytes_present']:,}**; free disk space: **{s['free_GiB']:.2f}GiB**. The exact current transfer/verification phase is retained in `acquisition_status.json` and the live download state.

The94 downloads are in progress as a detached resumable batch. The launch is not completion of the120-galaxy dataset. No new scientific image analysis has been performed, including on final-test galaxies; verification only checks archive integrity. Network access succeeded outside the restricted sandbox after its DNS failure. No API credential or signed URL is present in the outputs. No current blocker is recorded when the PID probe above is true.

Validation passed:120 distinct IDs, exact86/14/20 disjoint roles, all old26 confined to development, frozen CSV hashes, complete94-object size/range preflight, and six inherited downloader safety/integrity/resume tests under the expansion configuration. See `verification.log`. The sample is deliberately balanced in mass/activity. Gas fraction and gas surface-density proxies do not establish dust content, morphology or disk classification. Previously inspected feasibility galaxies cannot serve as the untouched final test.
'''
(OUT/'acquisition_report.md').write_text(report)
print(json.dumps(s,indent=2))
