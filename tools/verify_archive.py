#!/usr/bin/env python3
"""Read-only archive checks. Never imports or runs project scientific code."""
import argparse,csv,hashlib,json,os,re,subprocess,sys
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['PROJECT_STATE','SCIENTIFIC_DECISIONS','COMPLETED_ANALYSES','FAILED_EXPERIMENTS','OPEN_QUESTIONS','DATA_PROVENANCE','ML_EVALUATION_PROTOCOL','INSTRUMENTAL_ASSUMPTIONS','PUBLICATION_PLAN','PROJECT_HISTORY','NEW_SESSION_HANDOFF','GITHUB_SYNC_REPORT']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
 rows=list(csv.DictReader((ROOT/'docs/manifests/FILE_INVENTORY.csv').open()));original={r['path']:r for r in rows}
 errors=[];missing_excluded=[];hashed=0;metadata_checked=0
 for r in rows:
  p=ROOT/r['path'];inc=r['include']=='True'
  if not p.exists() and not p.is_symlink():
   if inc:errors.append({'type':'missing_original','path':r['path']})
   else:missing_excluded.append(r['path'])
   continue
  s=p.lstat();metadata_checked+=1
  if s.st_size!=int(r['bytes']):errors.append({'type':'size_changed','path':r['path']})
  # Git clones cannot preserve original mtimes; enforce mtime only on the original server root.
  if str(ROOT)=='/home/bahareh/ULTIMATE' and s.st_mtime_ns!=int(r['mtime_ns']):errors.append({'type':'mtime_changed','path':r['path']})
  if r['sha256'] and not p.is_symlink() and '/.venv/' not in r['path']:
   hashed+=1
   if sha(p)!=r['sha256']:errors.append({'type':'original_hash_changed','path':r['path']})
 for name in REQUIRED:
  if not (ROOT/'docs'/f'{name}.md').exists():errors.append({'type':'missing_required_document','path':name})
 for name in ['README.md','AGENTS.md','.gitignore','.gitattributes','requirements-archive.txt']:
  if not (ROOT/name).exists():errors.append({'type':'missing_required_file','path':name})
 eligible={r['path'] for r in rows if r['include']=='True'}
 # Only roots explicitly authored for this archive are added to original screened selections.
 new={str(p.relative_to(ROOT)) for folder in ['docs','tools'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 new.update(['README.md','AGENTS.md','.gitignore','.gitattributes','requirements-archive.txt'])
 allowed=eligible|new
 secret_rules={
  'private_key':r'-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----',
  'github_token':r'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b',
  'aws_access_id':r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
  'slack_token':r'\bxox[baprs]-[A-Za-z0-9-]{20,}',
  'signed_query':r'https?://[^\s<>"\x27]+[?&](?:X-Amz-Signature|access_token|api_key|token)=[A-Za-z0-9%_+/-]{16,}',
  'literal_credential':r'(?i)(?:api[_-]?key|password|secret[_-]?key|access[_-]?token)\s*[:=]\s*["\x27][A-Za-z0-9_+/=-]{20,}["\x27]'
 }
 scanned=0;secret_findings=[]
 for rel in sorted(allowed):
  p=ROOT/rel
  if not p.is_file():errors.append({'type':'allowlisted_missing','path':rel});continue
  if p.stat().st_size>25_000_000:errors.append({'type':'oversize','path':rel})
  if p.suffix in {'.png','.pdf','.npz','.joblib','.gz'}:continue
  content=p.read_text(errors='replace');scanned+=1
  # This checker's definitions are inert patterns, not credentials.
  if rel=='tools/verify_archive.py':continue
  # Original downloader test deliberately rejects this exact non-secret fixture URL.
  if rel=='data/TNG50_SKIRT_DR1_extra/test_downloader.py':
   content=content.replace('https://data-eu.tng-project.org/file?token=synthetic-test-key','https://data-eu.tng-project.org/file?token=<synthetic-fixture>')
  for name,pattern in secret_rules.items():
   markers={'private_key':['PRIVATE KEY'], 'github_token':['ghp_','github_pat_'], 'aws_access_id':['AKIA','ASIA'], 'slack_token':['xox'], 'signed_query':['?token=','&token=','access_token=','api_key=','X-Amz-Signature='], 'literal_credential':['api_key','api-key','password','secret_key','secret-key','access_token','access-token']}[name]
   candidate=content.lower() if name=='literal_credential' else content
   if not any(marker in candidate for marker in markers):continue
   if re.search(pattern,content):secret_findings.append({'path':rel,'rule':name})
 errors.extend({'type':'credential_pattern',**x} for x in secret_findings)
 # Resolve local Markdown links without executing/rendering any notebook.
 link_records=[]
 for rel in sorted(allowed):
  if not rel.endswith('.md'):continue
  p=ROOT/rel
  for match in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)',p.read_text()):
   target=match.group(1).strip().strip('<>')
   if target.startswith(('https:','http:','mailto:','#','data:')):continue
   target=unquote(target.split('#',1)[0]);q=(p.parent/target).resolve()
   try:qrel=str(q.relative_to(ROOT))
   except ValueError:qrel=str(q)
   status='included' if qrel in allowed or q.is_dir() else 'server_only_manifested' if qrel in original and original[qrel]['include']!='True' else 'missing'
   line=p.read_text()[:match.start()].count('\n')+1
   record={'document':rel,'line':line,'target':target,'resolved':qrel,'status':status};link_records.append(record)
   if status=='missing' and (rel.startswith('docs/') or rel in ['README.md','AGENTS.md']):errors.append({'type':'new_document_broken_link',**record})
 # Arithmetic/receipt inspection of saved results, without model.predict or refits.
 canon=ROOT/'analysis_results/ml_expanded_20261028'
 receipt=json.loads((canon/'FINAL_EVALUATION_COMPLETED.json').read_text())
 if receipt['final_evaluation_count']!=1 or receipt['rows']!=153600 or receipt['models_retuned']:errors.append({'type':'canonical_final_receipt'})
 frozen=sha(canon/'FINAL_PROTOCOL_FROZEN.json')
 if frozen!=receipt['freeze_sha256'] or frozen!='587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4':errors.append({'type':'canonical_freeze_hash'})
 perf=list(csv.DictReader((canon/'recommended_performance.csv').open()))
 for target,expected in {'A_g':.0741,'A_Ks':.0124,'dR50_Ks':.0799,'dC_Ks':.0887}.items():
  found=[r for r in perf if r['evaluation']=='final_test' and r['aperture']=='adaptive' and r['scenario']=='GLAO_NIR' and r['target']==target]
  if len(found)!=1 or round(float(found[0]['MAE']),4)!=expected:errors.append({'type':'headline_saved_table_mismatch','target':target})
 for scenario,expected in [('seeing_NIR',.1210),('GLAO_NIR',.0861)]:
  found=[r for r in perf if r['evaluation']=='final_test' and r['aperture']=='adaptive' and r['scenario']==scenario and r['target']=='dR50_Ks']
  if len(found)!=1 or round(float(found[0]['corrected_MAE']),4)!=expected:errors.append({'type':'corrected_radius_saved_table_mismatch','scenario':scenario})
 git={}
 try:
  git['head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
  git['branch']=subprocess.check_output(['git','symbolic-ref','--short','HEAD'],cwd=ROOT,text=True).strip()
  git['remote']=subprocess.check_output(['git','remote','get-url','origin'],cwd=ROOT,text=True).strip()
  tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))-{''}
  git['tracked_files']=len(tracked)
  for p in sorted(tracked-allowed):errors.append({'type':'unallowlisted_tracked_file','path':p})
  for p in sorted(allowed-tracked):errors.append({'type':'allowlisted_untracked_file','path':p})
  changed=subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT,text=True).splitlines();git['changed_tracked_files']=changed
 except subprocess.CalledProcessError:git['status']='No commit yet; precommit inspection only'
 report={'verified_date':'2026-10-29','scope':'Read-only archival checks; no scientific execution','original_files':len(rows),'original_metadata_checked':metadata_checked,'original_hashes_checked':hashed,'missing_excluded_expected_in_clone':len(missing_excluded),'eligible_originals':len(eligible),'allowlisted_files':len(allowed),'text_files_security_screened':scanned,'secret_pattern_findings':secret_findings,'links_checked':len(link_records),'historical_missing_links':[r for r in link_records if r['status']=='missing' and not r['document'].startswith('docs/') and r['document'] not in ['README.md','AGENTS.md']],'server_only_links':[r for r in link_records if r['status']=='server_only_manifested'],'canonical_final_count':receipt['final_evaluation_count'],'canonical_freeze_sha256':frozen,'saved_headline_table_checks':'pass' if not any('mismatch' in e['type'] for e in errors) else 'fail','git':git,'errors':errors,'status':'pass' if not errors else 'fail'}
 if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2));return 0 if not errors else 1
if __name__=='__main__':sys.exit(main())
