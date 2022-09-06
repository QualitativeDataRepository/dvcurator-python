#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  rename.py
#
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

# Create the name that will be used for the dropbox folder
def project_name(last_name, title):
	import re
	title = re.sub("Data for: ", '', title)
	title = re.sub("(Replication )?[Dd]ata for ", '', title)
	title = re.match("^(.+?\\s){1,5}", title).group(0).rstrip()
	title = re.sub("^[^a-zA-Z]?", "", title) # get rid of any beginning non-letter chars
	title = re.sub(":.+", '', title)
	folder_name = last_name + " - " + title
	special_characters = ['!','#','$','%', '&','@','[',']',']','_',':',';',"'"]
	for i in special_characters:
		folder_name = folder_name.replace(i,'')
	return folder_name

# Extract the last name of the first author (and second) for filename prefix
def last_name_prefix(citation):
    one = citation['author'][0]['authorName']['value'].split(", ")[0]
    if (len(citation['author'])==1):
        return one
    elif (len(citation['author'])==2):
        two = citation['author'][1]['authorName']['value'].split(", ")[0]
        return one + "-" + two
    else:
        return one + "-etal"

# Copy QDR prepared latest step to a new step, incrementing step number
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

# All the below functions are for the rename process
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

def remove_all_accents(folder):
    import unicodedata, os
    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, 
            unicodedata.normalize('NFKD', f).encode('ascii', 'ignore').decode('ascii')))

# This is the function we call from the GUI, which calls all the above
def basic_rename(dropbox, folder_name, prefix):
    new_path = copy_new_step(dropbox, folder_name, "rename")
    if (not new_path):
        return None
    add_filename_prefix(new_path, prefix)
    remove_all_accents(new_path)
    replace_spaces(new_path)
    return new_path