#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def make_metadata_folder(dropbox, folder_name):
	from glob import glob
	from shutil import copytree
	import os
	edit_path = os.path.normpath(os.path.join(dropbox, 'QDR Project - ' + folder_name, "QDR Prepared"))
	candidates = glob(os.path.join(edit_path, "[0-9]_[Rr]ename"))
	if (not candidates):
		print("Error: couldn't find #_rename folder")
		return None
	if (len(candidates) > 1):
		print("Error: multiple '#_rename' folders")
		return None

	# Increment folder number by 1 (e.g. 1_rename to 2_metadata)
	import_path = candidates[0]
	folder_number = os.path.split(import_path)[1]
	folder_number = int(folder_number[0]) + 1
	write_path = edit_path + "/%d_metadata" %folder_number

	if os.path.exists(write_path): # Don't overwrite
		print("Error: metadata folder already exists")
		return None

	# copy files to new folder
	copytree(import_path, write_path)
	
	return write_path

def find_pdfs(path):
	import os, re
	pdfs = []
	for root, dirs, files in os.walk(path):
		for name in files:
			if re.search('\.(pdf|PDF)', name):
				pdfs += [os.path.join(root, name)]

	return pdfs
	
def standard_metadata(edit_path, author):
	import pikepdf, os

	pdfs = find_pdfs(edit_path)
	if not pdfs:
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
				print("Warning: Edited PDF claims PDF/A")
			meta['dc:title'] = os.path.basename(path)
			#meta['dc:creator'] = author
			meta['pdf:Author'] = author
			meta['dc:description'] = "QDR Data Project"
			meta['pdf:Subject'] = "QDR Data Project"
			meta['pdf:Keywords'] = "-"

		pdf.save(path)
		print("Metadata written to '%s'" %path)
		#os.remove(original)

	#os.rmdir(old_path)
	return True

