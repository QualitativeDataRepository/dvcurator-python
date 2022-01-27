#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def make_metadata_folder(dropbox, folder_name):
	from glob import glob
	from shutil import copytree
	import os
	edit_path = dropbox + "/" + 'QDR Project - ' + folder_name + "/QDR Prepared"
	candidates = glob(edit_path + "/" + "[0-9]_[Rr]ename")
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

def standard_metadata(edit_path, author):
	from pdfrw import PdfReader, PdfWriter, PdfDict
	import os, re

	pdfs = []
	for root, dirs, files in os.walk(edit_path):
		for name in files:
			if re.search('\.(pdf|PDF)', name):
				pdfs += [os.path.join(root, name)]

	if not pdfs:
		return None
		
	for path in pdfs:
		title = os.path.basename(path)
		pdf = PdfReader(path)
		metadata = PdfDict(Author=author, Title=title, Keywords="-")
		pdf.Info.update(metadata)
		PdfWriter().write(path, pdf)
		#print("Metadata written to '%s'" %path)
