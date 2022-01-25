#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

def main(args=None):
	import sys, os, re
	if args is None:
		args=sys.argv
	
	from pkg_resources import resource_filename, resource_listdir

	config_file = ""
	doi = ""
	
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

	if not config_file:
		sys.exit()

	import configparser
	config = configparser.ConfigParser()
	config.read(config_file)
	host = config['default']['host']
	gh_repo = config['default']['repo']
	dv_token = config['default']['dataverse_token']
	gh_token = config['default']['github_token']
	dropbox = config['default']['dropbox']

	if not doi:
		doi = raw_input('DOI? (e.g. "doi:10.xxx/xxxx"): ')

	# Get metadata from dataverse
	import dvcurator.dataverse
	citation=dvcurator.dataverse.get_citation(host, doi, dv_token)
	last_name = citation['depositor'].split(', ')[0]
	
	short_title = citation['title']
	short_title = re.sub("(Replication )?[Dd]ata for ", '', short_title)
	short_title = re.match("^(.+?\\s){1,5}", short_title).group(0).rstrip()
	short_title = re.sub("^[^a-zA-Z]?", "", short_title) # get rid of any beginning non-letter chars
	short_title = re.sub(":.+", '', short_title)
	folder_name = last_name + " - " + short_title

	import dvcurator.github
	# Search for an existing github project. If there isn't one, create one
	existing = dvcurator.github.search_existing(folder_name, gh_repo, gh_token)
	if (existing):
		print("Looks like a github project already exists for this. Might want to check on that.")
		return

	print("Downloading dataset from dataverse, this may take a while...")
	edit_path = dvcurator.dataverse.download_dataset(host, doi, dv_token, folder_name, dropbox)
	print("Files downloaded and extracted to: " + edit_path)

	# Edit PDF metadata
	# import dvcurator.pdf_metadata
	# dvcurator.pdf_metadata(edit_path, citation['depositor']) 

	# Create github project + issues
	project = dvcurator.github.create_project(doi, citation, folder_name, gh_repo, gh_token)
	# Get internal issue templates
	issues = resource_listdir("dvcurator", "issues/")
	for issue in issues:
		issue = resource_filename("dvcurator", "issues/" + issue)
		dvcurator.github.add_issue(folder_name, issue, gh_repo, project, gh_token)

	print("Finished!")
	return
	
#if __name__ == '__main__':
#	import requests
#	import re
#	import os
#	import sys
#	sys.exit(main(sys.argv))
