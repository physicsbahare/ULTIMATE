#!/home/bahareh/miniforge3/envs/phd/bin/python
"""Credential-safe, sequential, resumable TNG50-SKIRT DR1 acquisition only."""
import argparse,fcntl,gzip,hashlib,json,os,re,shutil,signal,stat,sys,tarfile,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlsplit,unquote
from urllib.error import HTTPError,URLError
ROOT=Path('/home/bahareh/ULTIMATE');OUT=ROOT/'data/TNG50_SKIRT_DR1_extra';PIDFILE=ROOT/'tng50_dr1_download.pid'
CAP=65*2**30;MINFREE=100*2**30;SAFETY=256*2**20;CHUNK=4*2**20;STOP=False
URL='https://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/{}/skirt/skirt_atlas.tar.gz'
class SafeFailure(Exception):pass
class Pause(SafeFailure):pass
class AuthFailure(SafeFailure):pass
class SafeRedirect(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  target=urlsplit(newurl)
  if target.scheme!='https' or target.hostname not in ['www.tng-project.org','tng-project.org','data-eu.tng-project.org']:raise SafeFailure('Unapproved redirect; credential not forwarded')
  key=req.get_header('Api-key')
  if key and key in unquote(newurl):raise SafeFailure('Credential unexpectedly present in redirect URL; request blocked')
  redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
  if target.netloc!=urlsplit(req.full_url).netloc:redirected.remove_header('Api-key')
  return redirected
OPENER=build_opener(SafeRedirect())
def log(message):print(time.strftime('%Y-%m-%dT%H:%M:%S%z'),message,flush=True)
def atomic(path,obj):
 tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(obj,indent=2)+'\n');os.replace(tmp,path)
def credential():
 p=Path.home()/'.tng_api_key';s=p.stat()
 if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode)!=0o600 or s.st_uid!=os.getuid():raise AuthFailure('Credential must be an owner-only regular file with mode 600')
 key=p.read_text().strip()
 if not key or '\n' in key or '\r' in key:raise AuthFailure('Invalid credential-file format')
 return key

def request(sid,key,method='GET',start=None,end=None,validator=None):
 headers={'API-Key':key,'Accept-Encoding':'identity','User-Agent':'ULTIMATE-DR1-resumable-downloader/1.0'}
 if start is not None:headers['Range']=f'bytes={start}-'+(str(end) if end is not None else '')
 if validator:headers['If-Range']=validator
 return OPENER.open(Request(URL.format(int(sid)),headers=headers,method=method),timeout=120)
def retry_request(sid,key,method='GET',start=None,end=None,validator=None):
 for attempt in range(6):
  if STOP:raise Pause('Stop requested; partial retained')
  try:return request(sid,key,method,start,end,validator)
  except HTTPError as exc:
   data_host=urlsplit(exc.url).hostname=='data-eu.tng-project.org'
   if exc.code in [401,403] and not data_host:raise AuthFailure(f'Authentication/access failed at API: HTTP {exc.code}') from None
   if exc.code not in ([401,403,408,429,500,502,503,504] if data_host else [408,429,500,502,503,504]) or attempt==5:raise SafeFailure(f'HTTP {exc.code} at '+('archive data host' if data_host else 'API')) from None
   delay=min(120,5*2**attempt)
   after=exc.headers.get('Retry-After','')
   if after.isdigit():delay=min(300,max(delay,int(after)))
   log(f'id={sid} transient HTTP {exc.code}; retry in {delay}s')
  except (URLError,TimeoutError,ConnectionError,OSError) as exc:
   if attempt==5:raise SafeFailure('Connection failed after retries ('+type(exc).__name__+')') from None
   delay=min(120,5*2**attempt);log(f'id={sid} connection retry {attempt+1}/6 in {delay}s')
  for _ in range(delay):
   if STOP:raise Pause('Stop requested; partial retained')
   time.sleep(1)
 raise SafeFailure('HTTP retry limit reached')
def usage():return sum(x.stat().st_size for x in OUT.glob('TNG50_DR1_*.tar.gz*') if x.is_file())
def guard(extra=0):
 if usage()+extra>CAP:raise Pause('65 GiB compressed-archive budget reached; data retained')
 if shutil.disk_usage(OUT).free-extra<MINFREE+SAFETY:raise Pause('100 GiB free-space reserve plus safety margin reached; data retained')
 if STOP:raise Pause('Stop requested; partial retained')
def verify(path):
 """Read all regular tar payloads and force gzip EOF/CRC; never extract."""
 n=0;fits=0;uncompressed=0
 with gzip.open(path,'rb') as gz:
  with tarfile.open(fileobj=gz,mode='r|') as archive:
   for member in archive:
    if STOP:raise Pause('Stop requested during verification; archive retained')
    n+=1
    if member.isfile():
     fits+=int(member.name.lower().endswith(('.fits','.fit','.fits.gz')));stream=archive.extractfile(member);count=0
     while True:
      chunk=stream.read(CHUNK)
      if not chunk:break
      count+=len(chunk)
     if count!=member.size:raise SafeFailure('Tar member length mismatch')
     uncompressed+=count
  while gz.read(CHUNK):
   if STOP:raise Pause('Stop requested during gzip verification; archive retained')
 if n<1 or fits<1:raise SafeFailure('Archive contains no FITS image members')
 digest=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(CHUNK),b''):
   if STOP:raise Pause('Stop requested during checksum; archive retained')
   digest.update(chunk)
 return dict(sha256=digest.hexdigest(),tar_members=n,FITS_members=fits,uncompressed_regular_bytes=uncompressed,gzip_CRC='passed',tar_read='passed')
def manifest():
 a=json.loads((OUT/'selection_manifest.json').read_text());ids=[int(x['subhalo_id']) for x in a['selected']]
 if len(ids)!=25 or len(set(ids))!=25 or 294866 in ids:raise SafeFailure('Invalid selection: require 25 distinct extra DR1 IDs')
 if sum(int(x.get('expected_bytes',0)) for x in a['selected'])>CAP:raise Pause('Preflight archive total exceeds budget')
 return a

def preflight():
 key=credential();a=manifest();rows=[]
 # A bounded actual archive request proves usable access, gzip format and Range.
 sid=int(a['selected'][0]['subhalo_id'])
 for start in [0,1024]:
  with retry_request(sid,key,start=start,end=start+1023) as r:
   data=r.read(1024);cr=r.headers.get('Content-Range','');ctype=r.headers.get('Content-Type','').lower()
   if r.status!=206 or not cr.startswith(f'bytes {start}-{start+1023}/'):raise SafeFailure('Server did not demonstrate valid byte-range resume support')
   if start==0 and data[:2]!=b'\x1f\x8b':raise SafeFailure('Archive probe is not gzip')
   if len(data)!=1024:raise SafeFailure('Short archive probe')
   rows.append(dict(probe='archive_range',subhalo_id=sid,status=r.status,range_start=start,bytes_read=len(data),content_range=cr,content_type=ctype))
 def probe_item(item):
  sid=int(item['subhalo_id'])
  with retry_request(sid,key,start=0,end=1023) as r:
   cr=r.headers.get('Content-Range','');match=re.fullmatch(r'bytes 0-1023/(\d+)',cr);ctype=r.headers.get('Content-Type','').lower()
   if r.status!=206 or not match:raise SafeFailure(f'id={sid}: missing valid archive byte range')
   length=match[1];data=r.read(1024)
   if len(data)!=1024 or data[:2]!=b'\x1f\x8b':raise SafeFailure(f'id={sid}: archive probe failed gzip/length check')
   if 'html' in ctype or 'json' in ctype:raise SafeFailure(f'id={sid}: non-archive content type')
   item.update(expected_bytes=int(length),etag=r.headers.get('ETag'),last_modified=r.headers.get('Last-Modified'))
   return dict(probe='archive_range_size',subhalo_id=sid,status=r.status,expected_bytes=int(length),content_type=ctype,bytes_read=len(data))
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(probe_item,item):item for item in a['selected']}
  for future in as_completed(futures):
   result=future.result();rows.append(result);item=futures[future]
   log(f'Preflight id={item["subhalo_id"]}: {item["expected_bytes"]/2**30:.3f} GiB')
   atomic(OUT/'preflight_progress.json',dict(completed_size_probes=[x for x in rows if x['probe']=='archive_range_size']))
 total=sum(x['expected_bytes'] for x in a['selected']);free=shutil.disk_usage(OUT).free
 if total>CAP:raise Pause(f'Selected archive total {total/2**30:.3f} GiB exceeds 65 GiB cap')
 if free-total<MINFREE+SAFETY:raise Pause('Insufficient free space for all selected archives and reserve')
 a.update(expected_total_bytes=total,cap_bytes=CAP,min_free_bytes=MINFREE,preflight_free_bytes=free,preflight_time=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
 atomic(OUT/'selection_manifest.json',a);atomic(OUT/'preflight.json',dict(catalogue='official DR1 Baes24 atlas',authentication='passed; valid gzip archive byte ranges',probes=rows,expected_total_GiB=total/2**30,free_GiB=free/2**30))
 log(f'Preflight passed: 25 archives, {total/2**30:.3f} GiB total; free={free/2**30:.2f} GiB')

def download(item,key,state):
 sid=int(item['subhalo_id']);expected=int(item['expected_bytes']);path=OUT/f'TNG50_DR1_{sid}.tar.gz';part=path.with_name(path.name+'.part')
 record=state['galaxies'].get(str(sid),{})
 if path.exists():
  s=path.stat()
  if record.get('status')=='verified' and s.st_size==record.get('bytes') and s.st_mtime_ns==record.get('mtime_ns'):
   log(f'id={sid} skipping previously verified archive');return
  if s.st_size!=expected:raise SafeFailure('Existing archive size mismatch; preserved for inspection')
  log(f'id={sid} verifying existing archive before skip');result=verify(path)
  state['galaxies'][str(sid)]=dict(status='verified',bytes=s.st_size,mtime_ns=s.st_mtime_ns,**result);atomic(OUT/'download_state.json',state);return
 if part.exists() and part.stat().st_size>expected:raise SafeFailure('Partial exceeds expected byte length; preserved')
 for attempt in range(8):
  guard();offset=part.stat().st_size if part.exists() else 0
  if offset==expected:break
  state['current']=dict(subhalo_id=sid,phase='requesting',bytes=offset,expected_bytes=expected);atomic(OUT/'download_state.json',state)
  log(f'id={sid} requesting archive from byte {offset}; attempt {attempt+1}/8')
  try:
   etag=item.get('etag')
   validator=etag if etag and not etag.startswith('W/') else item.get('last_modified')
   with retry_request(sid,key,start=offset,validator=validator) as response:
    if response.status==206:
     cr=response.headers.get('Content-Range','');m=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',cr)
     if not m or int(m[1])!=offset or int(m[3])!=expected or int(m[2])!=expected-1:raise SafeFailure('Invalid resume Content-Range; partial retained')
    elif response.status==200 and offset==0:
     if int(response.headers.get('Content-Length',0))!=expected:raise SafeFailure('Archive length changed since preflight')
    else:raise SafeFailure('Server refused safe resume; partial retained')
    ctype=response.headers.get('Content-Type','').lower()
    if 'html' in ctype or 'json' in ctype:raise SafeFailure('Non-archive response; partial retained')
    log(f'id={sid} transfer starting at {offset} / {expected} bytes')
    last=offset;last_time=time.monotonic()
    with part.open('ab') as f:
     while True:
      data=response.read(min(CHUNK,expected-offset+1))
      if not data:break
      if offset+len(data)>expected:raise SafeFailure('Response exceeded expected length')
      guard(len(data));f.write(data);offset+=len(data)
      if offset-last>=128*2**20 or time.monotonic()-last_time>=60:
       state['current']=dict(subhalo_id=sid,phase='downloading',bytes=offset,expected_bytes=expected);atomic(OUT/'download_state.json',state)
       log(f'id={sid} {offset/2**30:.3f}/{expected/2**30:.3f} GiB ({100*offset/expected:.1f}%), free={shutil.disk_usage(OUT).free/2**30:.2f} GiB');last=offset;last_time=time.monotonic()
     f.flush();os.fsync(f.fileno())
   if offset!=expected:raise OSError('Short body')
   break
  except (OSError,URLError,TimeoutError,ConnectionError,__import__('http.client',fromlist=['IncompleteRead']).IncompleteRead) as exc:
   if attempt==7:raise SafeFailure('Stream failed after 8 resume attempts ('+type(exc).__name__+')') from None
   log(f'id={sid} stream interrupted ({type(exc).__name__}); partial retained, retry {attempt+1}/8');time.sleep(min(60,5*2**attempt))
 else:raise SafeFailure('Transfer retry limit reached')
 state['current']=dict(subhalo_id=sid,phase='verifying',bytes=expected);atomic(OUT/'download_state.json',state);log(f'id={sid} download finished; checking full gzip CRC and tar payloads')
 result=verify(part);os.replace(part,path);s=path.stat()
 state['galaxies'][str(sid)]=dict(status='verified',bytes=s.st_size,mtime_ns=s.st_mtime_ns,**result);state['current']=None;atomic(OUT/'download_state.json',state)
 log(f'id={sid} VERIFIED: {s.st_size/2**30:.3f} GiB, {result["FITS_members"]} FITS members')

def stop(signum,frame):
 global STOP
 STOP=True

def run():
 OUT.mkdir(exist_ok=True,parents=True)
 with (OUT/'.download.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise SafeFailure('Another downloader already owns the lock') from None
  PIDFILE.write_text(str(os.getpid())+'\n');signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
  a=manifest()
  if not (OUT/'preflight.json').exists():raise SafeFailure('Run successful preflight before batch')
  key=credential();guard();statefile=OUT/'download_state.json'
  state=json.loads(statefile.read_text()) if statefile.exists() else dict(galaxies={},current=None)
  state.update(status='running',pid=os.getpid(),started=time.strftime('%Y-%m-%dT%H:%M:%S%z'));atomic(statefile,state);log(f'DR1 batch PID={os.getpid()}; archive cap=65 GiB, free-space floor=100 GiB')
  failures=[]
  try:
   for item in a['selected']:
    sid=str(item['subhalo_id'])
    try:download(item,key,state)
    except (Pause,AuthFailure):raise
    except Exception as exc:
     # Only controlled exception text is logged; arbitrary exception messages
     # and response bodies/headers may contain secrets and are never printed.
     reason=str(exc) if isinstance(exc,SafeFailure) else type(exc).__name__
     state['galaxies'][sid]=dict(status='failed',reason=reason);failures.append(sid);atomic(statefile,state);log(f'id={sid} failed: {reason}; existing bytes preserved')
   state['status']='complete' if not failures else 'incomplete';state['current']=None
   log(f'Batch {state["status"]}: {sum(v.get("status")=="verified" for v in state["galaxies"].values())}/25 verified')
  except (Pause,AuthFailure) as exc:
   state.update(status='paused',reason=str(exc));log(str(exc))
  finally:state['updated']=time.strftime('%Y-%m-%dT%H:%M:%S%z');atomic(statefile,state)
if __name__=='__main__':
 try:
  if '--preflight' in sys.argv:preflight()
  else:run()
 except Exception as exc:
  log('Stopped: '+(str(exc) if isinstance(exc,SafeFailure) else type(exc).__name__));sys.exit(1)
