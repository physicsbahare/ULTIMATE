"""Offline safety/functional checks; never reads the real credential."""
import contextlib,gzip,io,json,os,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request
from urllib.error import HTTPError
import download_dr1 as d
class Response:
 def __init__(self,data,start=0,total=None,fail_after=None):
  self.stream=io.BytesIO(data);self.status=206;self.headers={'Content-Range':f'bytes {start}-{(total or len(data))-1}/{total or len(data)}','Content-Type':'application/gzip'};self.fail_after=fail_after;self.calls=0
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self,n):
  self.calls+=1
  if self.fail_after is not None:
   if self.calls>1:raise ConnectionResetError()
   return self.stream.read(min(n,self.fail_after))
  return self.stream.read(n)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.out=Path(self.tmp.name);self.ctx=patch.object(d,'OUT',self.out);self.ctx.start();d.STOP=False
  b=io.BytesIO()
  with tarfile.open(fileobj=b,mode='w') as t:
   data=os.urandom(4096);m=tarfile.TarInfo('test_O1_g.fits');m.size=len(data);t.addfile(m,io.BytesIO(data))
  self.payload=gzip.compress(b.getvalue())
 def tearDown(self):self.ctx.stop();self.tmp.cleanup()
 def test_resume_and_verified_skip(self):
  offsets=[]
  def reply(sid,key,start=0,**kwargs):
   offsets.append(start);return Response(self.payload[start:],start,len(self.payload),fail_after=100 if len(offsets)==1 else None)
  state={'galaxies':{},'current':None};item={'subhalo_id':123,'expected_bytes':len(self.payload)}
  with patch.object(d,'retry_request',side_effect=reply),patch.object(d,'guard'),patch.object(d.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):d.download(item,'synthetic-test-key',state)
  self.assertEqual(offsets,[0,100]);self.assertEqual((self.out/'TNG50_DR1_123.tar.gz').read_bytes(),self.payload);self.assertEqual(state['galaxies']['123']['gzip_CRC'],'passed')
  with patch.object(d,'retry_request',side_effect=AssertionError('network should be skipped')),patch.object(d,'verify',side_effect=AssertionError('unchanged verified file should be skipped')),contextlib.redirect_stdout(io.StringIO()):d.download(item,'synthetic-test-key',state)
 def test_broken_gzip_and_tar_rejected(self):
  path=self.out/'broken.gz';path.write_bytes(self.payload[:-8])
  with self.assertRaises((EOFError,gzip.BadGzipFile,tarfile.TarError)):d.verify(path)
  path.write_bytes(gzip.compress(b'x'*10240))
  with self.assertRaises(tarfile.TarError):d.verify(path)
 def test_budget_and_reserve(self):
  with patch.object(d,'usage',return_value=d.CAP):
   with self.assertRaises(d.Pause):d.guard(1)
  with patch.object(d,'usage',return_value=0),patch.object(d.shutil,'disk_usage',return_value=type('Disk',(),{'free':d.MINFREE+d.SAFETY})()):
   with self.assertRaises(d.Pause):d.guard(1)
 def test_redirect_safety(self):
  req=Request('https://www.tng-project.org/api/example',headers={'API-Key':'synthetic-test-key','Range':'bytes=0-1023'})
  handler=d.SafeRedirect();r=handler.redirect_request(req,None,302,'',{},'https://data-eu.tng-project.org/file?signature=placeholder')
  self.assertIsNone(r.get_header('Api-key'));self.assertEqual(r.get_header('Range'),'bytes=0-1023')
  for u in ['http://data-eu.tng-project.org/file','https://example.com/file','https://data-eu.tng-project.org/file?token=synthetic-test-key']:
   with self.assertRaises(d.SafeFailure):handler.redirect_request(req,None,302,'',{},u)
 def test_http_retry_and_auth_failure(self):
  exc=HTTPError('https://www.tng-project.org/',503,'',{},None);response=Response(b'x')
  with patch.object(d,'request',side_effect=[exc,response]),patch.object(d.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):self.assertIs(d.retry_request(1,'synthetic-test-key'),response)
  with patch.object(d,'request',side_effect=HTTPError('https://www.tng-project.org/',401,'',{},None)):
   with self.assertRaises(d.AuthFailure):d.retry_request(1,'synthetic-test-key')
 def test_existing_bad_size_preserved(self):
  path=self.out/'TNG50_DR1_123.tar.gz';path.write_bytes(b'x')
  with self.assertRaises(d.SafeFailure):d.download({'subhalo_id':123,'expected_bytes':20},'synthetic-test-key',{'galaxies':{}})
  self.assertEqual(path.read_bytes(),b'x')
if __name__=='__main__':unittest.main()
