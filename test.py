from importlib.metadata import metadata
import unittest, tempfile, os, shutil
from dvcurator import dataverse, github, pdf, rename, readme, fs

harvard_host = "https://dataverse.harvard.edu"
harvard_doi = "doi:10.7910/DVN/CZYY1N"
qdr_doi = "doi:10.5064/F6YYA3O3"
curation_repo = "QualitativeDataRepository/testing-demos"

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
		# these should all fail
		self.assertIsNone(dataverse.get_metadata("foobar", host=harvard_host))
		self.assertIsNone(dataverse.get_metadata("doi:foobar", host=harvard_host))
		self.assertIsNone(dataverse.get_metadata("doi:10.5064/F6FHTB9H"))
		self.assertIsNone(dataverse.get_metadata("doi:doi:doi:10.5064/F6FHTB9E"))
		# now let's test a success case
		metadata = dataverse.get_metadata(harvard_doi, host=harvard_host)
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		self.assertEqual(citation['title'], "Replication Data for: Data policies of highly-ranked social science journals")

	def test_biblio(self):
		self.assertTrue(dataverse.get_biblio_citation(qdr_doi).startswith("VandeVusse"))

	def test_download(self):
		f = tempfile.TemporaryDirectory()
		metadata = dataverse.get_metadata(qdr_doi)
		path = dataverse.download_dataset(metadata, f.name)
		self.assertTrue(os.path.isdir(path))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original Deposit.zip")))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original metadata.json")))
		self.assertTrue(os.path.exists(os.path.join(path, "README_VandeVusse-Mueller.txt")))
		# Try again, we should fail the second time
		self.assertIsNone(dataverse.download_dataset(metadata, f.name))
		f.cleanup()

		# try a harder example, with messed up filenames
		f = tempfile.TemporaryDirectory()
		metadata = dataverse.get_metadata("doi:10.5064/F68G8HMM")
		path = dataverse.download_dataset(metadata, f.name)
		self.assertTrue(os.path.isdir(path))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original Deposit.zip")))
		self.assertTrue(os.path.exists(os.path.join(path, os.pardir, os.pardir, "Original metadata.json")))
		f.cleanup()

class TestGithubAPI(unittest.TestCase):
	
	def test_check(self):
		self.assertTrue(github.check_repo(repo="IQSS/Dataverse"))
		self.assertFalse(github.check_repo(repo="Not/arealrepo"))
		
	def test_search(self):
		self.assertTrue(github.search_existing("Karcher - Anonymous Peer Review", repo="QualitativeDataRepository/testing-demos"))
		self.assertFalse(github.search_existing("Nobody - Project that doesnt exist", repo="QualitativeDataRepository/testing-demos"))

	def test_version(self):
		self.assertFalse(github.check_version())

class TestRename(unittest.TestCase):
	
	def test_projectname(self):
		# test limiting to before the first colon and removing "Data for:"
		metadata = dataverse.get_metadata("doi:10.5064/F6AQGERV")
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		self.assertEqual(rename.project_name(citation), "Haney - Child Support Adjudication")
		# try the limiting to 5 words feature
		metadata = dataverse.get_metadata("doi:10.5064/F6ZXIJS5")
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		self.assertEqual(rename.project_name(citation), "Guastaferro - Adapting a Selective Parent-Focused Child")
		# test special character removal
		metadata = dataverse.get_metadata("doi:10.5064/F6MBCJ8M")
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		self.assertEqual(rename.project_name(citation), "Berntzen - Monster or Hero Far-right Responses")
		# make a temporary directory named the citation and test it exists
		d = tempfile.TemporaryDirectory()
		new_folder_name = rename.project_name(citation)
		new_folder_path = os.path.join(d.name, new_folder_name, "QDR Prepared", "1_extract")
		os.makedirs(new_folder_path)
		self.assertTrue(os.path.exists(new_folder_path))  # Ensure it was successfully made
		d.cleanup()
		# test accented character removal
		metadata = dataverse.get_metadata("doi:10.5064/F6FHTB9E")
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		self.assertEqual(rename.project_name(citation), "Rabello Sodre - Memories about Colegio Sao Vicente")

	def test_rename(self):
		f = tempfile.TemporaryDirectory()
		first_folder = os.path.join(f.name, "QDR Prepared", "1_extract")
		os.makedirs(first_folder) 

		fake_file = "foobar.txt"
		with open(os.path.join(first_folder, fake_file), 'w') as fp:
			pass
		
		metadata = dataverse.get_metadata(harvard_doi, host=harvard_host)
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		new_path = rename.basic_rename(f.name, citation)
		new_file = os.listdir(new_path)[0]
		self.assertEqual(rename.last_name_prefix(citation) + "_" + fake_file,
			new_file)

		f.cleanup()
		
	def test_nameprefix(self):
		metadata = dataverse.get_metadata("doi:10.5064/F6YYA3O3")
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		self.assertEqual(rename.last_name_prefix(citation), "VandeVusse-Mueller")

		one_author_doi = "doi:10.7910/DVN/RHDI2C"
		metadata = dataverse.get_metadata(one_author_doi, host=harvard_host)
		citation = dataverse.get_citation(metadata)
		self.assertEqual(rename.last_name_prefix(citation), "Gadarian")

class TestPDFMetadata(unittest.TestCase):

	def test_nopdfs(self):
		self.assertFalse(pdf.standard_metadata("/notarealfolder", None))

		f = tempfile.TemporaryDirectory()
		edit_path = os.path.join(f.name, "QDR Prepared/5_Rename")
		os.makedirs(edit_path) 
		self.assertFalse(pdf.standard_metadata(edit_path, None))

		f.cleanup()

	def test_pdfmetadata(self):
		# This test is to make sure author string gets written
		# We read it back out from one of the files
		import pikepdf

		# Get author string from online citation
		metadata = dataverse.get_metadata(harvard_doi, host=harvard_host)
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)

		author_string = pdf.combine_author_names(citation)

		d = tempfile.TemporaryDirectory()
		temp_structure = os.path.normpath(os.path.join(d.name, "QDR Prepared/5_rename"))
		os.makedirs(temp_structure) 

		empty_pdf = pikepdf.Pdf.new()

		for i in range(1, 11):
			empty_pdf.save(os.path.join(temp_structure, f'test{i}.pdf'))

		edit_path = pdf.standard_metadata(d.name, citation)
		one_file = os.path.join(edit_path, os.listdir(edit_path)[4])
		example = pikepdf.open(one_file)
		meta = example.open_metadata()
		self.assertEqual(meta['pdf:Author'], author_string)
		example.close()

		d.cleanup()

	def test_anonmetadata(self):
		import pikepdf

		d = tempfile.TemporaryDirectory()
		temp_structure = os.path.normpath(os.path.join(d.name, "QDR Prepared", "5_something"))
		os.makedirs(temp_structure)

		empty_pdf = pikepdf.Pdf.new()

		for i in range(1, 11):
			empty_pdf.save(os.path.join(temp_structure, f'test{i}.pdf'))

		metadata = dataverse.get_metadata(harvard_doi, host=harvard_host)
		citation = dataverse.get_citation(metadata)
		self.assertIsNotNone(citation)
		new_path = rename.basic_rename(d.name, citation)

		new_path = fs.anonymize_project(d.name, citation)
		one_file = os.listdir(new_path)[4]
		print(one_file)
		self.assertTrue(one_file.startswith("ANONYMIZED"))
		example = pikepdf.open(os.path.join(new_path, one_file))
		meta = example.open_metadata()
		self.assertEqual(meta['pdf:Author'], "ANONYMIZED")
		example.close()

		d.cleanup()

class TestREADME(unittest.TestCase):

	def test_generateREADME(self):
		metadata = dataverse.get_metadata(harvard_doi, host=harvard_host)
		d=tempfile.TemporaryDirectory()
		subfolder = os.path.join(d.name, "5_ready")
		os.makedirs(subfolder)
		with open(os.path.join(subfolder, "a_file.txt"), 'w') as f:
			pass
		
		generated = readme.generate_readme(metadata, d.name, repo=curation_repo)
		self.assertTrue(os.path.exists(generated))
		# Fail on the second time
		self.assertIsNone(readme.generate_readme(metadata, d.name))

		d.cleanup()
		
if __name__ == '__main__':
	unittest.main()
