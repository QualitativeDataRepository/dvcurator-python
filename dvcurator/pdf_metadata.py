#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def find_pdfs(path):
	import os, re
	pdfs = []
	for root, dirs, files in os.walk(path):
		for name in files:
			if re.search('\.(pdf|PDF)', name):
				pdfs += [os.path.join(root, name)]

	return pdfs
	
def standard_metadata(folder, author):
	import pikepdf, os, shutil
	import dvcurator.fs

	edit_path = dvcurator.fs.copy_new_step(folder, "metadata")
	if not edit_path:
		return None

	pdfs = find_pdfs(edit_path)
	if not pdfs:
		print("Error: no PDFs detected in: " + edit_path)
		return None

	# Ideally, we would just edit the files in place
	# Some versions of pikepdf can't do this though
	# so we copy them to a separate folder, then save back to the orginal place
	old_path = os.path.join(edit_path, "originals")
	os.mkdir(old_path)
		
	for path in pdfs:
		original = os.path.join(old_path, os.path.basename(path))
		os.rename(path, original)
		pdf = pikepdf.open(original)
		# Clean out all existing metadata
		try:
			del pdf.Root.Metadata
			del pdf.docinfo
		except:
			pass
			
		# Write new metadata
		with pdf.open_metadata() as meta:
			if meta.pdfa_status:
				print("!! Warning !! PDF is PDF/A")
			meta['dc:title'] = os.path.basename(path)
			#meta['dc:creator'] = author
			meta['pdf:Author'] = author
			meta['dc:description'] = "QDR Data Project"
			meta['pdf:Subject'] = "QDR Data Project"
			meta['pdf:Keywords'] = "-"

		pdf.save(path)
		pdf.close()
		print("Metadata written to: %s" %os.path.basename(path))

	#os.rmdir(old_path)
	#shutil.rmtree(old_path)
	print("PDF metadata process complete!")

	return edit_path

