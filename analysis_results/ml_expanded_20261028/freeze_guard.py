"""Read-only artifact verification, without accessing any final science."""
import hashlib,json
from pathlib import Path

def verify():
    root=Path(__file__).resolve().parents[2]
    receipt=Path(__file__).resolve().parent/'FINAL_PROTOCOL_FROZEN.json'
    data=json.loads(receipt.read_text())
    assert data['protocol_frozen'] and data['allow_final_unseal']
    for item in data['artifacts']:
        p=root/item['path'];h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        assert h.hexdigest()==item['sha256'],f'Frozen artifact changed: {p}'
    return hashlib.sha256(receipt.read_bytes()).hexdigest()
