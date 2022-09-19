import unittest, tempfile, os, shutil
from dvcurator import dataverse, github, pdf_metadata, rename, fs

harvard_host = "https://dataverse.harvard.edu"
harvard_doi = "doi:10.7910/DVN/CZYY1N"

class TestFs(unittest.TestCase):

	def test_check_dropbox(self):
		self.assertFalse(fs.check_dropbox("/notarealfolder"))

		f = tempfile.TemporaryDirectory()
		os.makedirs(os.path.join(f.name, "QDR Project - Foobar"))
		self.assertTrue(fs.check_dropbox(f.name, "Foobar"))

		self.assertFalse(fs.check_dropbox(f.name, "Foobar-DoesntExist"))
		self.assertTrue(fs.check_dropbox(f.name))

		f.cleanup()


	def test_new_step(self):
		self.assertFalse(fs.copy_new_step("/notarealfolder", "test"))

		f = tempfile.TemporaryDirectory()
		first_folder = os.path.join(f.name, "QDR Prepared", "1_extract")
		self.assertFalse(fs.copy_new_step(f.name, "test"))

		os.makedirs(first_folder)
		self.assertTrue(fs.copy_new_step(f.name, "test"))

		f.cleanup()


class TestDataverseAPI(unittest.TestCase):
	
	def test_citation(self):
		self.assertIsNone(dataverse.get_citation("foobar", host=harvard_host))
		self.assertIsNone(dataverse.get_citation("doi:foobar", host=harvard_host))
		citation = dataverse.get_citation(harvard_doi, host=harvard_host)
		self.assertIsNotNone(citation)
		self.assertEqual(citation['title'], "Replication Data for: Data policies of highly-ranked social science journals")

	def test_download(self):
		f = tempfile.TemporaryDirectory()
		path = dataverse.download_dataset(harvard_doi, f.name, host=harvard_host)
		self.assertTrue(os.path.isdir(path))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original Deposit.zip")))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original metadata.json")))

		self.assertTrue(os.path.exists(os.path.join(path, "readme_CrosasEtal.txt")))
		
		f.cleanup()

class TestGithubAPI(unittest.TestCase):
	
	def test_check(self):
		self.assertTrue(github.check_repo(repo="IQSS/Dataverse"))
		self.assertFalse(github.check_repo(repo="Not/arealrepo"))
		
	def test_search(self):
		self.assertTrue(github.search_existing("Karcher - Anonymous Peer Review", repo="QualitativeDataRepository/testing-demos"))

	def test_version(self):
		self.assertFalse(github.check_version())

class TestRename(unittest.TestCase):
	
	def test_projectname(self):
		citation = dataverse.get_citation("doi:10.5064/F6AQGERV")
		self.assertIsNotNone(citation)
		self.assertEqual(rename.project_name(citation), "Haney - Child Support Adjudication")

	def test_rename(self):
		f = tempfile.TemporaryDirectory()
		first_folder = os.path.join(f.name, "QDR Prepared", "1_extract")
		os.makedirs(first_folder) 

		fake_file = "foobar.txt"
		with open(os.path.join(first_folder, fake_file), 'w') as fp:
			pass
		
		citation = dataverse.get_citation(harvard_doi, host=harvard_host)
		self.assertIsNotNone(citation)
		new_path = rename.basic_rename(f.name, citation)
		new_file = os.listdir(new_path)[0]
		self.assertEqual(rename.last_name_prefix(citation) + "_" + fake_file,
			new_file)

		f.cleanup()
		
	def test_nameprefix(self):
		citation = dataverse.get_citation("doi:10.5064/F6YYA3O3")
		self.assertIsNotNone(citation)
		self.assertEqual(rename.last_name_prefix(citation), "VandeVusse-Mueller")

		one_author_doi = "doi:10.7910/DVN/RHDI2C"
		citation = dataverse.get_citation(one_author_doi, host=harvard_host)
		self.assertEqual(rename.last_name_prefix(citation), "Gadarian")

class TestPDFMetadata(unittest.TestCase):

	def test_nopdfs(self):
		self.assertFalse(pdf_metadata.standard_metadata("/notarealfolder", None))

		f = tempfile.TemporaryDirectory()
		edit_path = os.path.join(f.name, "QDR Prepared/5_Rename")
		os.makedirs(edit_path) 
		self.assertFalse(pdf_metadata.standard_metadata(edit_path, None))

		f.cleanup()

	def test_pdfmetadata(self):
		# This test is to make sure author string gets written
		# We read it back out from one of the files
		import pikepdf

		# Get author string from online citation
		citation = dataverse.get_citation(harvard_doi, host=harvard_host)
		self.assertIsNotNone(citation)

		author_string = pdf_metadata.combine_author_names(citation)

		d = tempfile.TemporaryDirectory()
		temp_structure = os.path.normpath(os.path.join(d.name, "QDR Prepared/5_rename"))
		os.makedirs(temp_structure) 

		empty_pdf = pikepdf.Pdf.new()

		for i in range(1, 11):
			empty_pdf.save(os.path.join(temp_structure, f'test{i}.pdf'))

		edit_path = pdf_metadata.standard_metadata(d.name, citation)
		one_file = os.path.join(edit_path, os.listdir(edit_path)[4])
		example = pikepdf.open(one_file)
		meta = example.open_metadata()
		self.assertEqual(meta['pdf:Author'], author_string)
		example.close()

		d.cleanup()
		
if __name__ == '__main__':
	unittest.main()
