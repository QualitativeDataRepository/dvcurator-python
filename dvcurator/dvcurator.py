#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

def project_name(last_name, title):
	title = re.sub("(Replication )?[Dd]ata for ", '', title)
	title = re.match("^(.+?\\s){1,5}", title).group(0).rstrip()
	title = re.sub("^[^a-zA-Z]?", "", title) # get rid of any beginning non-letter chars
	title = re.sub(":.+", '', title)
	folder_name = last_name + " - " + title
	return folder_name

def main(args=None):
	import sys, os, re
	if args is None:
		args=sys.argv
	
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

	# Import config file
	if not config_file:
		print("Needs config file!")
		sys.exit()

	import configparser
	config = configparser.ConfigParser()
	config.read(config_file)
	host = config['default']['host']
	gh_repo = config['default']['repo']
	dv_token = config['default']['dataverse_token']
	gh_token = config['default']['github_token']
	dropbox = config['default']['dropbox']

	# Get metadata from dataverse
	from dvcurator import dataverse
	citation=dataverse.get_citation(host, doi, dv_token)
	last_name = citation['depositor'].split(', ')[0]
	
	folder_name = project_name(last_name, citation['title'])

	from dvcurator import github
	# Search for an existing github project. If there isn't one, create one
	existing = github.search_existing(folder_name, gh_repo, gh_token)
	if (existing):
		print("Looks like a github project already exists for this. Might want to check on that.")
		return

	# Download and extract
	print("Downloading dataset from dataverse, this may take a while...")
	edit_path = dataverse.download_dataset(host, doi, dv_token, folder_name, dropbox)
	print("Files downloaded and extracted to: " + edit_path)

	# Edit PDF metadata
	# from dvcurator import pdf_metadata
	# pdf_metadata(edit_path, citation['depositor']) 

	from pkg_resources import resource_filename, resource_listdir
	# Create github project + issues
	project = github.create_project(doi, citation, folder_name, gh_repo, gh_token)
	# Get internal issue templates
	issues = resource_listdir("dvcurator", "issues/")
	for issue in issues:
		issue = resource_filename("dvcurator", "issues/" + issue)
		github.add_issue(folder_name, issue, gh_repo, project, gh_token)

	print("Finished!")
	return
	
#if __name__ == '__main__':
#	import requests
#	import re
#	import os
#	import sys
#	sys.exit(main(sys.argv))
