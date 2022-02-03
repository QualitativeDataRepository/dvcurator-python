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
		return None
	if (len(candidates) > 1):
		print("Error: multiple '#_rename' folders")
		return None

	import_path = candidates[0]
	folder_number = os.path.split(import_path)[1]
	folder_number = int(folder_number[0]) + 1
	write_path = edit_path + "/%d_metadata" %folder_number

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
		
	for path in pdfs:
		pdf = pikepdf.open(path)
		# Clean out all existing metadata
		#del pdf.Root.Metadata
		#def pdf.docinfo

		with pdf.open_metadata() as meta:
			meta['dc:title'] = os.path.basename(path)
			meta['dc:creator'] = author
			meta['pdf:Author'] = author
			meta['dc:description'] = "QDR Data Project"
			meta['pdf:Subject'] = "QDR Data Project"
			meta['pdf:Keywords'] = "-"
		
		pdf.save(path)
		return True
		#print("Metadata written to '%s'" %path)
