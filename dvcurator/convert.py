#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  convert.py
#  
#  Copyright 2022 Michael McCall <mimccall@syr.edu>
#

def docx_pdf(path):
    from docx2pdf import convert
    convert(path)
