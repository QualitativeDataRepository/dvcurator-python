import unittest, tempfile, os, shutil
from dvcurator import dataverse, github, pdf_metadata, rename, fs

host = "dataverse.harvard.edu"
doi = "doi:10.7910/DVN/CZYY1N"
#host = "data.qdr.syr.edu"
#doi = "doi:10.5064/F6RQA7AQ"

class TestDataverseAPI(unittest.TestCase):
	
	def test_citation(self):
		self.assertIsNone(dataverse.get_citation(host, "foobar"))
		self.assertIsNone(dataverse.get_citation(host, "doi:foobar"))
		citation = dataverse.get_citation(host, doi)
		self.assertEqual(citation['title'], "Replication Data for: Data policies of highly-ranked social science journals")

	def test_download(self):
		f = tempfile.TemporaryDirectory()
		path = dataverse.download_dataset(host, doi, f.name)
		self.assertTrue(os.path.isdir(path))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original Deposit.zip")))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original metadata.json")))

		self.assertTrue(os.path.exists(os.path.join(path, "readme_CrosasEtal.txt")))
		
		f.cleanup()

class TestGithubAPI(unittest.TestCase):
	
	def test_check(self):
		self.assertTrue(github.check_repo("IQSS/Dataverse"))
		self.assertFalse(github.check_repo("Not/arealrepo"))
		
	def test_search(self):
		self.assertTrue(github.search_existing("Karcher - Anonymous Peer Review", "QualitativeDataRepository/testing-demos"))

class TestPDFMetadata(unittest.TestCase):

	def test_makedir(self):
		f = tempfile.TemporaryDirectory()
		os.makedirs(os.path.join(f.name, "QDR Prepared/5_Rename")) 
		new_path = fs.copy_new_step(f.name, "Unit Test")
		self.assertTrue(new_path)
		f.cleanup()

	def test_pdfmetadata(self):
		# This test is to make sure test_string gets written
		# We read it back out from one of the files
		import pikepdf
		test_string = "Unit Test"
		d = tempfile.TemporaryDirectory()
		temp_structure = os.path.normpath(os.path.join(d.name, "QDR Prepared/5_rename"))
		os.makedirs(temp_structure) 

		empty_pdf = pikepdf.Pdf.new()

		for i in range(1, 11):
			empty_pdf.save(os.path.join(temp_structure, f'test{i}.pdf'))

		edit_path = pdf_metadata.standard_metadata(d.name, test_string)
		one_file = os.path.join(edit_path, os.listdir(edit_path)[4])
		example = pikepdf.open(one_file)
		meta = example.open_metadata()
		self.assertEqual(meta['pdf:Author'], test_string)
		example.close()

		d.cleanup()
		
if __name__ == '__main__':
	unittest.main()
