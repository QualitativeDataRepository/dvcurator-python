#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  convert.py
#  
#  Copyright 2022 Michael McCall <mimccall@syr.edu>
#

def docx_pdf(folder, extra=None):
    """
    Convert all docx files in a folder to PDFs

    :param folder: Folder to convert docx files in
    :type folder: Path, as String
    """
    import dvcurator.fs, os, glob, pythoncom
    from docx2pdf import convert
    
    pythoncom.CoInitialize()

    path = dvcurator.fs.copy_new_step(folder, "convert")
    if not path:
        return None
        
    print("Converting docx files...")
    convert(path)

    files = glob.glob(os.path.join(path, "*.docx"))
    for f in files:
        os.remove(f)
        
    print("Done!")
