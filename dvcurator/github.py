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

	try:
		projects.raise_for_status()		
	except requests.exceptions.HTTPError as http_err:
		print(f"HTTP error occurred: {http_err}")
		print(f"Response Content: {projects.content}")
		return True
	except Exception as err:
		print(f"Other error occurred: {err}")
		return True

	# Issue titles are "<project name> - <task>", so match on the project name.
	# Collapse whitespace, since existing tickets aren't consistent about it
	project_name = ' '.join(project_name.split())

	for project in projects.json():
		name = ' '.join(project['title'].split())
		if (name == project_name or name.startswith(project_name + " - ")):
			return True

	# Return false if nothing was found
	return False

def wait_for_project_run(repo, headers, since, timeout=180):
	"""
	Wait for the workflow run that our dispatch just started.

	A workflow_dispatch returns no run id, so we look for the newest run
	created since we sent the request and then follow that one.

	:param repo: Github repository path (e.g. QualitativeDataRepository/Project-Curation)
	:type repo: String
	:param headers: Request headers, including the authorization token
	:type headers: dict
	:param since: Ignore any run created before this
	:type since: datetime, timezone aware
	:param timeout: Seconds to wait before giving up
	:type timeout: int
	:return: The completed run, or None if it never finished
	:rtype: dict, or None
	"""
	import requests, time
	from datetime import datetime

	runs_url = github_api + "/repos/" + repo + "/actions/workflows/new_project.yml/runs"
	deadline = time.time() + timeout
	run_id = None

	# First find the run. It takes a few seconds to show up in the API
	while (time.time() < deadline and not run_id):
		try:
			runs = requests.get(runs_url + "?event=workflow_dispatch&per_page=10", headers=headers)
			runs.raise_for_status()
			runs = runs.json()['workflow_runs']
		except Exception as err:
			print(f"Could not check on the workflow run: {err}")
			return None

		# The API returns these newest first
		for run in runs:
			created = datetime.fromisoformat(run['created_at'].replace("Z", "+00:00"))
			if (created >= since):
				run_id = run['id']
				break
		if not run_id:
			time.sleep(3)

	if not run_id:
		print("Timed out waiting for the workflow to start.")
		return None

	# Then wait for it to finish
	run_url = github_api + "/repos/" + repo + "/actions/runs/" + str(run_id)
	while (time.time() < deadline):
		try:
			run = requests.get(run_url, headers=headers)
			run.raise_for_status()
			run = run.json()
		except Exception as err:
			print(f"Could not check on the workflow run: {err}")
			return None

		if (run['status'] == "completed"):
			return run
		time.sleep(5)

	print("Timed out waiting for the workflow to finish.")
	return None

def project_url_from_run(repo, run, headers):
	"""
	Dig the project number out of a completed run's log and build its URL.

	The workflow echoes "Made project number: N", which is the only place
	the number is exposed to us.

	:param repo: Github repository path
	:type repo: String
	:param run: Completed run, as returned by `wait_for_project_run()`
	:type run: dict
	:param headers: Request headers, including the authorization token
	:type headers: dict
	:return: URL of the new project, or None if the log didn't have it
	:rtype: String, or None
	"""
	import requests, re

	try:
		jobs = requests.get(github_api + "/repos/" + repo + "/actions/runs/" + str(run['id']) + "/jobs",
			headers=headers)
		jobs.raise_for_status()
		job = jobs.json()['jobs'][0]

		log = requests.get(github_api + "/repos/" + repo + "/actions/jobs/" + str(job['id']) + "/logs",
			headers=headers)
		log.raise_for_status()
	except Exception as err:
		print(f"Could not read the workflow log: {err}")
		return None

	number = re.search(r"Made project number: (\d+)", log.text)
	if not number:
		return None

	org = repo.split("/")[0]
	return "https://github.com/orgs/" + org + "/projects/" + number.group(1)

def create_project(dv, project_name, token, repo=None):
	"""
    Trigger a "create a project" workflow in a GitHub repository.

    :param project_name: The name of the project to be created.
    :type project_name: str
    :param token: The GitHub API token for authentication.
    :type token: str
    :param repo: The repository where the project will be created. If not provided, the default repository will be used.
    :type repo: str, optional
    :return: URL of the new project, or None if it wasn't created
    :rtype: String, or None
    """
	import requests, dvcurator.hosts, dvcurator.dataverse
	from datetime import datetime, timezone, timedelta
	repo = dvcurator.hosts.curation_repo if not repo else repo

	if (search_existing(project_name, token, repo)):
		print("Error: Project already exists or search failed")
		return

	doi = dv['data']['latestVersion']['datasetPersistentId']
	dataset_contact = dvcurator.dataverse.get_citation(dv)['datasetContact'][0]['datasetContactName']['value']
	link = dvcurator.hosts.qdr_doi_path + doi
	contact_info = 'Depositor: ' + dataset_contact + '\n'
	contact_info += 'DV link: ' + link

	url = github_api + "/repos/" + repo + "/actions/workflows/new_project.yml/dispatches"
	headers = {
		"Accept": "application/vnd.github.v3+json",
		"Content-Type": "application/json",
		"X-GitHub-Api-Version": "2022-11-28",
		"Authorization": f"token {token}"
	}
	data = {
		"ref": "master",
		"inputs": {
			"title": project_name,
			"desc": link,
			"readme": contact_info
		}
	}
	
	# Note the time before dispatching, so we can pick our run out afterwards.
	# Back it off a little to allow for clock differences
	since = datetime.now(timezone.utc) - timedelta(seconds=10)

	try:
		response = requests.post(url, headers=headers, json=data)
		response.raise_for_status()
	except requests.exceptions.HTTPError as http_err:
		print(f"HTTP error occurred: {http_err}")
		print(f"Response Content: {response.content}")
		return None
	except Exception as err:
		print(f"Other error occurred: {err}")
		return None

	# A dispatch only means github accepted the request. The project is created
	# by the workflow, which can still fail, so wait and report what happened
	print("Request sent, waiting for github to create the project...")
	run = wait_for_project_run(repo, headers, since)
	if not run:
		print("Couldn't confirm whether the project was created.")
		print("Check the repository's Actions tab before trying again.")
		return None

	if (run['conclusion'] != "success"):
		print("Error: project creation failed on github.")
		print("Run log: " + run['html_url'])
		print("This is usually an expired credential, not a problem with your")
		print("own token. Contact a repository admin.")
		return None

	project = project_url_from_run(repo, run, headers)
	if not project:
		print("Project created, but its number wasn't in the log.")
		print("Run log: " + run['html_url'])
		return None

	print("Created project: " + project)
	return project