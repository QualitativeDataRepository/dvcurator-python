import unittest, tempfile, os
from dvcurator import pdf_metadata

class TestPDFMetadata(unittest.TestCase):
	
	def test_pdfmetadata(self):
		d = tempfile.TemporaryDirectory()

		for i in range(1, 11):
			with open(os.path.join(d.name, f'test{i}.pdf'), 'w'):
				pass

		pdf_metadata.pdf_metadata(d.name, "Test")
		d.cleanup()
		
if __name__ == '__main__':
	unittest.main()

