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

# Generate the string for the author metadata field
# separate with semicolons between full names for > 1 author
def combine_author_names(citation):
	author_string = citation['author'][0]['authorName']['value']
	if (len(citation['author']) > 1):
		for author in citation['author'][1:]:
			author_string += "; " + author['authorName']['value']
	return author_string

# This is the function run from the GUI
def standard_metadata(folder, citation):
	import pikepdf, os, shutil
	import dvcurator.fs

	edit_path = dvcurator.fs.copy_new_step(folder, "metadata")
	if not edit_path:
		return None

	pdfs = find_pdfs(edit_path)
	if not pdfs:
		print("Error: no PDFs detected in: " + edit_path)
		return None

	author_string = combine_author_names(citation)

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
			meta['pdf:Author'] = author_string
			meta['dc:description'] = "QDR Data Project"
			meta['pdf:Subject'] = "QDR Data Project"
			meta['pdf:Keywords'] = "-"

		pdf.save(path)
		pdf.close()
		print("Metadata written to: %s" %os.path.basename(path))

	shutil.rmtree(old_path)
	print("PDF metadata process complete!")

	return edit_path

