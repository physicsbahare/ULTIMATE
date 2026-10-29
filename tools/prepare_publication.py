#!/usr/bin/env python3
"""Prepare an explicit archive allowlist; never stages or alters scientific files."""
import argparse,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECEIPTS={'docs/manifests/PUBLISHED_FILES.csv','docs/manifests/ARCHIVE_VERIFICATION.json','docs/manifests/REMOTE_VERIFICATION.json','docs/GITHUB_SYNC_REPORT.md'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--allowlist',type=Path,required=True);args=ap.parse_args()
 baseline=list(csv.DictReader((ROOT/'docs/manifests/FILE_INVENTORY.csv').open()))
 originals={r['path']:r for r in baseline if r['include']=='True'}
 paths=set(originals)
 for directory in ['docs','tools']:
  paths.update(str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 paths.update(['README.md','AGENTS.md','.gitignore','.gitattributes','requirements-archive.txt','docs/manifests/PUBLISHED_FILES.csv'])
 rows=[]
 for path in sorted(paths):
  p=ROOT/path
  if path in RECEIPTS:size='';digest=''
  else:
   size=p.stat().st_size
   if size>25_000_000:raise ValueError(f'Oversize allowlisted file: {path}')
   digest='' if path in RECEIPTS else hashlib.sha256(p.read_bytes()).hexdigest()
  rows.append({'path':path,'bytes':size,'sha256':digest,'origin':'original' if path in originals else 'archive_documentation','hash_policy':'Git object is authoritative for final receipts/self-reference' if path in RECEIPTS else 'SHA-256 current content'})
 with (ROOT/'docs/manifests/PUBLISHED_FILES.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['path','bytes','sha256','origin','hash_policy']);w.writeheader();w.writerows(rows)
 args.allowlist.write_bytes(b''.join(r['path'].encode()+b'\0' for r in rows))
 print(json.dumps({'files':len(rows),'originals':len(originals),'allowlist':str(args.allowlist),'known_bytes':sum(int(r['bytes']) for r in rows if r['bytes']!='')},indent=2))
if __name__=='__main__':main()
