#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def search_existing(project_name, repo, key):
	import json, requests
	github='https://api.github.com'
	key = {'Authorization': "token " + key}
	workflow='main'

	project_url = github + "/repos/" + repo + "/projects"
	projects = requests.get(project_url + "?per_page=100", headers=key)

	project_name = ' '.join(project_name.split()[:3])

	for project in projects.json():
		name = project['name']
		search_token = ' '.join(name.split()[:3])
		if (project_name == search_token):
			project_id = project['id']
			columns_url = github + "/projects/%d/columns" % (project_id)
			print(columns_url)
			return requests.get(columns_url, headers=key)

	# Return none if nothing was found
	return None

def create_project(metadata, folder_name, repo, key):
	import json, requests, os, re

	github='https://api.github.com'
	key = {'Authorization': "token " + key}
	workflow='main'

	project_url = github + "/repos/" + repo + "/projects"
	#existing_projects = requests.get(project_url, headers=key)
	#for project in existing_projects:

	contact_info = 'Name:' + metadata['depositor'] + '\n'
	contact_info += 'DV link: https://data.qdr.syr.edu/dataset.xhtml?persistentId=' + "doi"

	metadata = { 'name': folder_name, 'body': contact_info }
	project = requests.post(project_url, json.dumps(metadata), headers=key)
	project_id = project.json()['id']
	print("Created github project: " + folder_name)
	
	# Make a Todo, in progress and done column
	column_url = github + "/projects/%d/columns" % (project_id)
	columns = []
	for column in ['To Do', 'In Progress', 'Done']:
		metadata = { 'name': column }
		resp = requests.post(column_url, json.dumps(metadata), headers=key)
		columns += [resp.json()['id']]

	return columns[0] # This is the ID of the todo column, for assigning issue cards

def add_issue(project_name, template, repo, project, key):
	import os, json, requests, re
	
	github='https://api.github.com'
	key = {'Authorization': "token " + key}

	# Format issue name from template filename
	issue_name = os.path.basename(template)
	issue_name = re.sub('\.md', '', issue_name)
	issue_name = re.sub('_', ' ', issue_name)

	# Import the markdown file as the issue body
	f = open(template, "r")
	body = f.readlines()
	issue_url = github + "/repos/" + repo + "/issues"
	metadata = {'title': project_name + " - " + issue_name, 'body': ''.join(body) }
	resp = requests.post(issue_url, json.dumps(metadata), headers=key)
	issue = resp.json()['id']

	metadata = {'content_type': "Issue", 'content_id': issue}
	card_url = github + "/projects/columns/%d/cards" % (project)
	resp = requests.post(card_url, json.dumps(metadata), headers=key)

	print("Issue created: " + project_name + " _ " + issue_name)
