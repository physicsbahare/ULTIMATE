"""Final reproducibility receipt; original archive hashes are in archive_inventory.csv."""
from pathlib import Path
import sys,json,hashlib,platform,datetime,importlib.metadata
O=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','astropy','pandas','matplotlib','nbformat','nbclient','nbconvert','ipykernel']}
 code={p.name:sha(p) for p in O.glob('*.py')}
 record=dict(created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),executable=sys.executable,python=platform.python_version(),versions=versions,code_sha256=code,protocol_sha256=sha(O/'PROTOCOL.md'),development_gate_protocol_sha256=json.loads((O/'development_gate.json').read_text())['protocol_sha256'],data_policy='Existing local archives only; no packages installed; no science datasets downloaded; no ML or geometry fitting',sampling_unit='galaxy',development_IDs=[294866,167418,626287,535051,638950],evaluation_galaxies=21,noise_draws=8,galaxy_bootstrap_draws=5000,bootstrap_seed=20261027,legacy_import_restoration_receipt='legacy_PDF_restoration.json',validation=json.loads((O/'validation.json').read_text()))
 assert record['protocol_sha256']==record['development_gate_protocol_sha256']
 (O/'execution_provenance.json').write_text(json.dumps(record,indent=2))
 files=[p for p in O.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='output_manifest.sha256']
 (O/'output_manifest.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(O)}\n' for p in sorted(files)))
 print('Recorded',len(files),'output hashes; package versions and protocol match.')
if __name__=='__main__':run()
