#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  rename.py
#
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

def copy_new_step(dropbox, folder_name, step):
    import os.path
    from shutil import copytree
    from glob import glob
    edit_path = os.path.normpath(os.path.join(dropbox, 'QDR Project - ' + folder_name, "QDR Prepared"))
    candidates = glob(os.path.join(edit_path, "[0-9]_*"))
    if (len(candidates) < 1):
        return None
    current = candidates[len(candidates)-1]
    number = int(os.path.split(current)[1].split("_")[0]) + 1
    new_step = str(number) + "_" + step
    copytree(os.path.join(edit_path, current), os.path.join(edit_path, new_step))
    return os.path.join(edit_path, new_step)

def add_filename_prefix(folder, prefix):
    import os
    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, ''.join([prefix + "_", f])))

def replace_spaces(folder):
    import os
    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, f.replace(" ", "_")))

def basic_rename(dropbox, folder_name, prefix):
    new_path = copy_new_step(dropbox, folder_name, "rename")
    add_filename_prefix(new_path, prefix)
    replace_spaces(new_path)
    return new_path