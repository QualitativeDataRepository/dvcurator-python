#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

github_api='https://api.github.com'

# Is there a more recent version of 
def check_version():
	import requests, dvcurator.version, dvcurator.hosts
	tags_url = github_api + "/repos/" + dvcurator.hosts.pkg_repo + "/tags"
	tags = requests.get(tags_url).json()
	latest = tags[0]['name']
	if (dvcurator.version.version != latest):
		if (dvcurator.version.version == "git-development"):
			print("Running development version")
		else:
			print("! Alert: update available:\n" + "https://github.com/" + dvcurator.hosts.pkg_repo + "/releases")
		return False
	else:
		return True

# Check if repository specified actually exists
# False = Doesn't exist, True = exists
def check_repo(key=None, repo=None):
	import requests, dvcurator.hosts
	repo = dvcurator.hosts.curation_repo if not repo else repo
	project_url = github_api + "/repos/" + repo + "/issues"
	if (not key):
		projects = requests.get(project_url + "?per_page=100")
	else:
		key = {'Authorization': "token " + key}
		projects = requests.get(project_url + "?per_page=100", headers=key)

	if (projects.status_code==404):
		return False
	else:
		return True

# Search if tickets already exist in the repo for this project
# True = tickets exist, False = they don't exist
def search_existing(project_name, key=None, repo=None):
	import json, requests, dvcurator.hosts

	repo = dvcurator.hosts.curation_repo if not repo else repo 
	project_url = github_api + "/repos/" + repo + "/issues"

	# Ideally we would use the project API endpoint here.
	# We can't, because it requires an OAuth token for all calls
	# even on public repositories. So we go directly to the issues
	if (not key):
		projects = requests.get(project_url + "?per_page=100")
	else:
		key = {'Authorization': "token " + key}
		projects = requests.get(project_url + "?per_page=100", headers=key)
				
	# Take the first three words ("lastname - first-of-title") to search
	project_name = ' '.join(project_name.split()[:3])

	for project in projects.json():
		name = project['title']
		# Tokenize all the project names the same way (first 3 words)
		search_token = ' '.join(name.split()[:3])
		if (project_name == search_token): # Return column ID if found
			return True
			
	# Return false if nothing was found
	return False

def create_project(doi, metadata, folder_name, repo, key):
	import json, requests, os, re, dvcurator.hosts

	key = {'Authorization': "token " + key}
	workflow='main'

	project_url = github_api + "/repos/" + repo + "/projects"

	contact_info = 'Name:' + metadata['depositor'] + '\n'
	contact_info += 'DV link: ' + dvcurator.hosts.qdr_doi_path + doi

	metadata = { 'name': folder_name, 'body': contact_info }
	project = requests.post(project_url, json.dumps(metadata), headers=key)
	project_id = project.json()['id']
	#print("Created github project: " + folder_name)
	
	# Make a Todo, in progress and done column
	column_url = github_api + "/projects/%d/columns" % (project_id)
	columns = []
	for column in ['To Do', 'In Progress', 'Done']:
		metadata = { 'name': column }
		resp = requests.post(column_url, json.dumps(metadata), headers=key)
		columns += [resp.json()['id']]

	return columns[0] # This is the ID of the todo column, for assigning issue cards

def add_issue(project_name, template, repo, project, key):
	import os, json, requests, re
	
	key = {'Authorization': "token " + key}

	# Format issue name from template filename
	issue_name = os.path.basename(template)
	issue_name = re.sub('\.md', '', issue_name)
	issue_name = re.sub('_', ' ', issue_name)

	# Import the markdown file as the issue body
	f = open(template, "r")
	body = f.readlines()
	issue_url = github_api + "/repos/" + repo + "/issues"
	metadata = {'title': project_name + " - " + issue_name, 'body': ''.join(body) }
	resp = requests.post(issue_url, json.dumps(metadata), headers=key)
	issue = resp.json()['id']

	metadata = {'content_type': "Issue", 'content_id': issue}
	card_url = github_api + "/projects/columns/%d/cards" % (project)
	resp = requests.post(card_url, json.dumps(metadata), headers=key)

	#print("Issue created: " + project_name + " _ " + issue_name)

# This is the actual function we run from the buttom
def generate_template(doi, citation, folder_name, token, issues_selected, repo=None):
	import os.path, sys, dvcurator.hosts
	from pkg_resources import resource_filename

	repo = dvcurator.hosts.curation_repo if not repo else repo 

	if not check_repo(token):
		print("Error: github repository doesn't exist")
		return None

	if search_existing(folder_name, token):
		print("Error: existing github issues!!")
		return None

	project = create_project(doi, citation, folder_name, repo, token)
	print("Created project: " + folder_name)
	# Get internal issue templates from selected checkboxes
	for issue in issues_selected:
		path = issue.get()
		if (path != "0"):
			if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
				path = os.path.join(sys._MEIPASS, "issues", path)
			else:
				path = resource_filename("dvcurator", "issues/" + path)
			add_issue(folder_name, path, repo, project, token)
			print(issue.get() + " added to project")
