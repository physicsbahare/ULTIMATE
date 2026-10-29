import unittest,sys
from pathlib import Path
class ImportIsolation(unittest.TestCase):
 def test_new_renderer_stays_local_after_legacy_import(self):
  import observe
  import presentation
  self.assertEqual(Path(presentation.__file__).resolve().parent,Path(__file__).resolve().parent)
if __name__=='__main__':unittest.main()
