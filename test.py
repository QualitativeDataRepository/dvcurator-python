import unittest, tempfile, os
from dvcurator import dataverse, github, pdf_metadata

host = "dataverse.harvard.edu"
doi = "doi:10.7910/DVN/CZYY1N"
#host = "data.qdr.syr.edu"
#doi = "doi:10.5064/F6RQA7AQ"

class TestDataverseAPI(unittest.TestCase):
	
	def test_citation(self):
		citation = dataverse.get_citation(host, doi)
		self.assertEqual(citation['title'], "Replication Data for: Data policies of highly-ranked social science journals")

	def test_download(self):
		f = tempfile.TemporaryDirectory()
		path = dataverse.download_dataset(host, doi, "", "Unit Test", f.name)

		self.assertTrue(os.path.isdir(path))
		self.assertTrue(os.path.exists(os.path.join(path, "..", "Original Deposit.zip")))
		self.assertTrue(os.path.exists(os.path.join(path, "readme_CrosasEtal.txt")))
		
		f.cleanup()
		
if __name__ == '__main__':
	unittest.main()
