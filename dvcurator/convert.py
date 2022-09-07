#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  convert.py
#  
#  Copyright 2022 Michael McCall <mimccall@syr.edu>
#

def docx_pdf(folder, suffix=None):
    import dvcurator.fs
    from docx2pdf import convert
    import os, glob

    path = dvcurator.fs.copy_new_step(folder, "convert")
    if not path:
        return None

    convert(path)
    files = glob.glob(os.path.join(path, "*.docx"))
    for f in files:
        os.remove(f)

