#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

github_api='https://api.github.com'

# Is there a more recent version of the program?
def check_version():
	"""
	Check whether the running version is the same as the newest github tag

	:return: Whether a new update is available on github
	:rtype: boolean
	"""
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
	"""
	Check whether github repository exists

	:param key: Github API key, or None for public repository
	:type key: String or None
	:param repo: Github repository path (e.g. QualitativeDataRepository/dvcurator-python), or None for default
	:type repo: String or None
	:return: Whether or not the repository is accessible
	:rtype: boolean
	"""
	import requests, dvcurator.hosts
	repo = dvcurator.hosts.curation_repo if not repo else repo
	project_url = github_api + "/repos/" + repo + "/issues"
	if (not key):
		projects = requests.get(project_url + "?per_page=100")
	else:
		key = {'Authorization': "token " + key.strip()}
		projects = requests.get(project_url + "?per_page=100", headers=key)

	if (projects.status_code==404):
		return False
	else:
		return True

# Search if tickets already exist in the repo for this project
# True = tickets exist, False = they don't exist
def search_existing(project_name, token=None, repo=None):
	"""
	Check if a project has existing github tickets

	:param project_name: Project name to check for existing tickets
	:type project_name: String
	:param token: Github token key, or None for public repository
	:type token: String or None
	:param repo: Github repository path (e.g. QualitativeDataRepository/dvcurator-python), or None for default
	:type repo: String or None
	:return: Whether or not there are any existing tickets with the specified project name
	:rtype: boolean
	"""
	import json, requests, dvcurator.hosts

	repo = dvcurator.hosts.curation_repo if not repo else repo 
	project_url = dvcurator.hosts.github_api + "/repos/" + repo + "/issues"

	# Ideally we would use the project API endpoint here.
	# We can't, because it requires an OAuth token for all calls
	# even on public repositories. So we go directly to the issues
	if (not token):
		projects = requests.get(project_url + "?per_page=100")
	else:
		token = {'Authorization': "token " + token.strip()}
		projects = requests.get(project_url + "?per_page=100", headers=token)

	projects.raise_for_status()

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

def create_project(dv, project_name, token, repo=None):
	"""
    Trigger a "create a project" workflow in a GitHub repository.

    :param project_name: The name of the project to be created.
    :type project_name: str
    :param token: The GitHub API token for authentication.
    :type token: str
    :param repo: The repository where the project will be created. If not provided, the default repository will be used.
    :type repo: str, optional
    :return: A dictionary containing the response from the GitHub API.
    :rtype: dict
    :raises requests.exceptions.RequestException: If there is an error with the HTTP request.
    """
	import requests, dvcurator.hosts, dvcurator.dataverse
	repo = dvcurator.hosts.curation_repo if not repo else repo 

	if (search_existing(project_name, token, repo)):
		print("Project already exists")
		return

	doi = dv['data']['latestVersion']['datasetPersistentId']
	link = dvcurator.hosts.qdr_doi_path + doi
	contact_info = 'Depositor: ' + dvcurator.dataverse.get_citation(dv)['depositor'] + '\n'
	contact_info += 'DV link: ' + link


	url = "https://api.github.com/repos/" + repo + "/dispatches"
	headers = {
		"Accept": "application/vnd.github.everest-preview+json",
		"Content-Type": "application/json",
		"Authorization": f"token {token}"
	}
	data = {
		"event_type": "trigger-event",
		"client_payload": {
			"title": project_name,
			"desc": link,
			"readme": contact_info
		}
	}

	response = requests.post(url, headers=headers, json=data)
	response.raise_for_status() 