#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

def short_title(title):
	title = re.sub("(Replication )?[Dd]ata for: ", '', title)
	title = re.match("^(.+?\\s){1,5}", title).group(0).rstrip()
	return re.sub(":.+", '', title)

def main(args):
	from glob import glob
	
	host="data.qdr.syr.edu"
	gh_repo="QualitativeDataRepository/Project-Curation"

	import getopt
	args = args[1:]
	shortopts = "d:v:g:f:"
	longopts = ['doi', 'dvtoken', 'ghtoken', 'folder']
	options, args = getopt.getopt(args, shortopts, longopts)

	for opt, val in options:
		if opt in('-d', '--doi'):
			doi = val
		elif opt in ('-v', '--dvtoken'):
			dv_token = val
		elif opt in ('-g', '--ghtoken'):
			gh_token = val
		elif opt in ('-f', '--folder'):
			dropbox = val
	
	citation=get_citation(host, doi, dv_token)
	last_name = citation['depositor'].split(', ')[0]
	folder_name = last_name + " - " + short_title(citation['title'])

	edit_path = download_dataset(host, doi, dv_token, folder_name, dropbox)
	pdf_metadata(edit_path, citation['depositor'])

	project = create_project(citation, folder_name, gh_repo, gh_token)

	# If we only specify a directory, use all the files in it as issue templates
	if os.path.isdir(args[0]):
		args = os.path.join(args[0], '*.md')
		args = glob(args)	

	for issue in args:
		add_issue(folder_name, issue, gh_repo, project, gh_token)

	print("Finished!")
	
if __name__ == '__main__':
	import requests
	import re
	import os
	import sys
	from dataverse import *
	from github import *
	from pdf_metadata import *
	sys.exit(main(sys.argv))
