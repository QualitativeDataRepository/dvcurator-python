#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

def main(args):
	from api import dataverse
	from api import github
	from files import pdf_metadata
	
	from glob import glob
	import configparser
	#from pkg_resources import resource_listdir
	
	import getopt
	args = args[1:]
	shortopts = "c:d:"
	longopts = ['config', 'doi']
	options, args = getopt.getopt(args, shortopts, longopts)

	for opt, val in options:
		if opt in ('-c', '--config'):
			config_file = val
		elif opt in('-d', '--doi'):
			doi = val

	config = configparser.ConfigParser()
	config.read(config_file)
	host = config['default']['host']
	gh_repo = config['default']['repo']
	dv_token = config['default']['dataverse_token']
	gh_token = config['default']['github_token']
	dropbox = config['default']['dropbox']
	
	citation=get_citation(host, doi, dv_token)
	last_name = citation['depositor'].split(', ')[0]
	
	short_title = citation['title']
	short_title = re.sub("(Replication )?[Dd]ata for ", '', short_title)
	short_title = re.match("^(.+?\\s){1,5}", short_title).group(0).rstrip()
	short_title = re.sub("^[^a-zA-Z]?", "", short_title) # get rid of any beginning non-letter chars
	short_title = re.sub(":.+", '', short_title)
	folder_name = last_name + " - " + short_title

	edit_path = download_dataset(host, doi, dv_token, folder_name, dropbox)
	# pdf_metadata(edit_path, citation['depositor']) 

	project = create_project(citation, folder_name, gh_repo, gh_token)

	# for now, args is the internal issues directory
	#args = pkg_resources.resource_listdir("dvcurator", "issues") 

	# If we only specify a directory, use all the files in it as issue templates
	if os.path.isdir(args[0]):
		args = os.path.join(args[0], '*.md')
		args = glob(args)	

	for issue in args:
		add_issue(folder_name, issue, gh_repo, project, gh_token)

	print("Finished!")
	
#if __name__ == '__main__':
#	import requests
#	import re
#	import os
#	import sys
#	sys.exit(main(sys.argv))
