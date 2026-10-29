import unittest,tempfile,gzip
from pathlib import Path
from audit_sample import gzip_crc
class CRCChecks(unittest.TestCase):
 def test_trailer_corruption_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.gz';raw=b'scientific integrity\n'*100;p.write_bytes(gzip.compress(raw));self.assertEqual(gzip_crc(p),len(raw))
   b=bytearray(p.read_bytes());b[-8]^=1;p.write_bytes(b)
   with self.assertRaises(gzip.BadGzipFile):gzip_crc(p)
if __name__=='__main__':unittest.main()
