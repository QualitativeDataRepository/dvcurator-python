#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  rename.py
#
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

def project_name(citation):
    """
    Generate project name string, used in dropbox folder name and github project name

    :param citation: Citation block generated by `get_citation()`
    :return: String to use as the folder name or project name
    :rtype: String

    """
    import re

    author1_last_name = citation['author'][0]['authorName']['value'].split(', ')[0]
    title = citation['title']
    title = re.sub("Data for: ", '', title)
    title = re.sub("(Replication )?[Dd]ata for ", '', title)
    title = re.match("^(.+?\\s){1,5}", title).group(0).rstrip()
    title = re.sub("^[^a-zA-Z]?", "", title) # get rid of any beginning non-letter chars
    title = re.sub(":.+", '', title)
    
    folder_name = author1_last_name + " - " + title

    special_characters = ['!','#','$','%', '&','@','[',']',']','_',':',';',"'"]
    for i in special_characters:
        folder_name = folder_name.replace(i,'')
        
    return folder_name

def last_name_prefix(citation):
    """
    Extract the last name of the first author (and second) for filename prefix

    :param citation: Citation block generated by `get_citation()`
    :return: String of last name (or other prefix if >1 author)
    :rtype: String
    """
    one = citation['author'][0]['authorName']['value'].split(", ")[0]
    if (len(citation['author'])==1):
        return one
    elif (len(citation['author'])==2):
        two = citation['author'][1]['authorName']['value'].split(", ")[0]
        return one + "-" + two
    else:
        return one + "-etal"

# All the below functions are for the rename process
def add_filename_prefix(folder, prefix):
    """
    Add a prefix to all files in a folder

    :param folder: Folder to rename files in
    :type folder: Path, as string
    :param prefix: Prefix to add to filenames
    :type prefix: String
    """
    import os
    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, ''.join([prefix + "_", f])))

def replace_spaces(folder):
    """
    Remove spaces in all filenames in a folder

    :param folder: Folder to rename files in
    :type folder: Path, as string
    """
    import os
    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, f.replace(" ", "_")))

def remove_all_accents(folder):
    """
    Remove all accented characters in filenames in a folder

    :param folder: Folder to rename files in
    :type folder: Path, as string
    """
    import unicodedata, os

    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, 
            unicodedata.normalize('NFKD', f).encode('ascii', 'ignore').decode('ascii')))

# This is the function we call from the GUI, which calls all the above
def basic_rename(folder, citation):
    """
    Run a series of operations to properly format filenames in a folder according to QDR guidelines. 
    Add prefix, remove accents, replace spaces.

    :param folder: Folder to rename files in
    :type folder: Path, as string
    :param citation: Citation block generated by `get_citation()`
    :return: Path to the new folder with renamed files
    :rtype: String
    """
    import dvcurator.fs
    print("Renaming files", end="... ")
    prefix = last_name_prefix(citation)
    new_path = dvcurator.fs.copy_new_step(folder, "rename")
    if (not new_path):
        return None
    add_filename_prefix(new_path, prefix)
    remove_all_accents(new_path)
    replace_spaces(new_path)
    print("Done!")
    return new_path

def anonymize(folder, citation):
    """
    Anonymize the filenames, replacing names with ANONYMIZED

    :param folder: folder of the files to rename
    :type folder: path, as string
    :param citation: Citation block generated by `get_citation()`
    """
    import os
    print("Renaming files", end="... ")
    remove_string = last_name_prefix(citation)
    for i, f in enumerate(os.listdir(folder)):
        os.rename(os.path.join(folder, f), os.path.join(
            folder, f.replace(remove_string, "ANONYMIZED")))