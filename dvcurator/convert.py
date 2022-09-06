#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  convert.py
#  
#  Copyright 2022 Michael McCall <mimccall@syr.edu>
#

from dvcurator.rename import copy_new_step


def docx_pdf(dropbox, folder_name):
    import dvcurator.rename
    from docx2pdf import convert
    import os, glob

    path = dvcurator.rename.copy_new_step(dropbox, folder_name, "convert")
    convert(path)
    files = glob.glob(os.path.join(path, "*.docx"))
    for f in files:
        os.remove(f)

