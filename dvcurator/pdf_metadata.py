#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def pdf_metadata(edit_path, author):
	from pdfrw import PdfReader, PdfWriter, PdfDict
	
	pdfs = []
	for f in os.listdir(edit_path):
		if re.search('\.(pdf|PDF)', f):
			pdfs += [f]

	for path in pdfs:
		path = os.path.join(edit_path, path)
		pdf = PdfReader(path)
		metadata = PdfDict(Author=author, Title=path, Subject="-")
		pdf.Info.update(metadata)
		PdfWriter().write(path, pdf)
		print("Metadata written to '%s'" %path)
