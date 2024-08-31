#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

github_api='https://api.github.com'

def gql_query(query, token, params=None):
	"""
	Run a gql API query on Github

	:param query: The gql query
	:type query: string
	:param token: Github API token
	:type token: string
	:param params: Parameters to pass to the gql query
	:type params: dict
	:return: The response from the API
	"""
	from gql import Client, gql
	from gql.transport.aiohttp import AIOHTTPTransport

	query = gql(query)

	transport = AIOHTTPTransport(
		url = github_api + "/graphql",
		headers = {'Authorization': "token " + token.strip()}
	)
	client = Client(transport=transport, fetch_schema_from_transport=True)

	if params:
		results = client.execute(query, variable_values=params)
	else:
		results = client.execute(query)

	return results

def get_org_id(endpoint, token=None):
	"""
	Get the ID of an organization

	:param endpoint: Name of the organization
	:type endpoint: string
	:param token: Github API token
	:type token: string
	:return: Organization github ID
	:rtype: string
	"""
	import requests
	url = github_api + "/orgs/" + endpoint
	if not token:
		info = requests.get(url)
	else:
		token = {'Authorization': "token " + token.strip()}
		info = requests.get(url, headers=token)

	if not info.ok:
		return None

	return info.json()['node_id']

def get_team_id(team, token, org=None):
	"""
	Get node ID of a team

	:param team: Name of the team (slug format, i.e. "Curation and recruitment" becomes "curation-and-recruitment")
	:type team: string
	:param token: Github API token
	:type token: string
	:param org: Github organization, defaults to `github_org` in `hosts.py`
	:type org: string
	:return: Node ID of the team
	:rtype: string
	"""
	import requests
	import dvcurator.hosts
	if not org:
		org = dvcurator.hosts.github_org

	url = github_api + "/orgs/" + org + "/teams"
	token = {'Authorization': "token " + token}
	info = requests.get(url, headers=token)

	#return info.json()
	teams = info.json()
	slugs = []
	ids = []
	for t in teams:
		slugs += [t['slug']]
		ids += [t['node_id']]

	return ids[slugs.index(team)]

def get_repo(token, search, repo=None):
	"""
	Get the ID of a repository

	:param token: Github API token
	:type token: string
	:param search: Name of a project to search for an existing one
	:type search: string
	:param repo: Github repository (e.g. QualitativeDataRepository/dvcurator-python)
	:type repo: string
	:return: ID of the repository, or none if an existing project is detected
	:rtype: string
	"""
	import dvcurator.hosts
	print("Checking for existing github projects...")
	query =	"""
		query ($org: String!, $repo: String!, $query: String!) {
			repository(owner: $org, name: $repo) {
				id
				projectsV2 (first: 20, query: $query) {
					nodes {
						id
						title
					}
				}
			}
		}
		"""

	if not repo:
		repo_components = dvcurator.hosts.curation_repo.split("/")
	else:
		repo_components = repo.split("/")

	params = {"org": repo_components[0], "repo": repo_components[1], "query": search}
	response = gql_query(query, token, params)

	if (len(response['repository']['projectsV2']['nodes']) > 0):
		print("Error: existing github project detected!")
		return None
	else:
		return response['repository']['id']


# This function is used to set each generated ticket to "todo" status
def alter_column(project_id, item_id, field_id, option_id, token):
	"""
	Put a created issue into a different column

	:param project_id: Project ID
	:type project_id: string
	:param item_id: Issue ID
	:type item_id: string
	:param field_id: ID of the columns option
	:type field_id: string
	:param option_id: ID of the option to change to (i.e. which column)
	:type option_id: string
	:param token: Github API token
	:type token: string
	:return: results of API query
	"""
	from gql import gql

	query = """
		mutation ($PROJECT_ID: ID!, $ITEM_ID: ID!, $FIELD_ID: ID!, $OPTION_ID: String!) {
			updateProjectV2ItemFieldValue(input: { 
				projectId: $PROJECT_ID
				itemId: $ITEM_ID 
				fieldId: $FIELD_ID 
				value: { singleSelectOptionId: $OPTION_ID }}) { 
					projectV2Item { 
						id 
					}
			}
		}
		"""

	params={"PROJECT_ID": project_id, "ITEM_ID": item_id, "FIELD_ID": field_id, "OPTION_ID": option_id}
	return gql_query(query, token, params)

def draft_issue(pid, template, token):
	"""
	Create a draft issue in a project based on a template

	:param pid: Github project ID
	:type pid: String
	:param template: Path to template txt file
	:type template: Path, as string
	:param token: Github API token
	:type token: string
	:return: ID of draft issue
	:rtype: string
	"""
	import os, re

	# Format issue name from template filename
	issue_name = os.path.basename(template)
	issue_name = re.sub('\.md', '', issue_name)
	issue_name = re.sub('_', ' ', issue_name)
	issue_name = issue_name.title()

	# Import the markdown file as the issue body
	f = open(template, "r")
	body = f.readlines()

	query = """
		mutation ($pid: ID!, $title: String!, $body: String!) {
			addProjectV2DraftIssue(input: {projectId: $pid, title: $title, body: $body})
			{projectItem {id}}
		} 
		"""

	params={"pid": pid, "title": issue_name, "body": ''.join(body)}

	project = gql_query(query, token, params)
	print("Added draft issue: " + issue_name)
	return project['addProjectV2DraftIssue']['projectItem']['id']

# This makes the project itself
# And returns all the variable fields of the new project
def new_projectv2(dv, title, token):
	"""
	Create new github project (version 2)

	:param dv: Dataverse metadata block from `get_metadata()`
	:param title: Title of the project
	:type title: string
	:param token: Github API token
	:type token: string
	:return: ProjectV2 object from API
	"""
	import dvcurator.hosts, dvcurator.dataverse

	repo = get_repo(token, title)
	if not repo: # detected existing project
		return None

	query = """
		mutation ($id: ID!, $title: String!) {
			createProjectV2(input: {ownerId: $id, title: $title})
			{projectV2 {				
				... on ProjectV2 { 
					id
					fields(first: 20) { 
						nodes { 
							... on ProjectV2Field { id name } 
							... on ProjectV2IterationField { id name configuration { 
								iterations { startDate id }}} 
								... on ProjectV2SingleSelectField { id name options { id name }}}}}}}
		} 
		"""

	qdr_id = get_org_id("QualitativeDataRepository")
	params={"id": qdr_id, "title": title}
	project = gql_query(query, token, params)
	print("Created project...")

	# Now we run the mutation to change the project description
	doi = dv['data']['latestVersion']['datasetPersistentId']
	link = dvcurator.hosts.qdr_doi_path + doi
	contact_info = 'Depositor: ' + dvcurator.dataverse.get_citation(dv)['depositor'] + '\n'
	contact_info += 'DV link: ' + link

	query = """
		mutation ($pid: ID!, $readme: String!, $desc: String!, $team: ID!) {
			updateProjectV2( input: {projectId: $pid, readme: $readme, shortDescription: $desc}) {
				projectV2 {id}
			} linkProjectV2ToRepository( input: {projectId: $pid, repositoryId: $team}) {
				repository {homepageUrl}
			}

		}
		"""

	params = {"pid": project['createProjectV2']['projectV2']['id'], "readme": contact_info, "desc": link, "team": repo}
	gql_query(query, token, params)
	print("Added description to project...")

	# then assign it to the team! (or repo in this case)
	#team = get_team_id("curation-and-recruitment", token)
	#		linkProjectV2ToTeam( input: {projectId: $pid, teamId: $team})
	return project['createProjectV2']['projectV2']

# This is the actual function we run from the buttom
def generate_templatev2(dv, project_name, token):
	"""
	Create new github project and associated tickets for a project

	:param dv: Dataverse metadata block from `get_metadata()`
	:param project_name: Project name (used as prefix)
	:type project_name: string
	:param token: Github API token
	:type token: string
	"""
	import os, sys, dvcurator.hosts, dvcurator.github
	from pkg_resources import resource_filename

	# create the project
	project = new_projectv2(dv, project_name, token)
	if not project: # detected existing project
		return None

	columns = project['fields']['nodes'][2]

	# "issues" folder location differs depending on whether or not this is run as a pyinstaller compiled file
	folder = os.path.join("assets", "issues")
	if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
		folder = os.path.join(sys._MEIPASS, folder)
		issues = [os.path.join(folder, f) for f in os.listdir(folder)]
	else:
		folder += "/"
		from pkg_resources import resource_listdir, resource_filename
		issues = [resource_filename(__name__, folder + f) for f in resource_listdir(__name__, folder)]

	# Get internal issue templates
	for issue in issues:
		draft = add_issue(project_name, issue, dvcurator.hosts.curation_repo, project['id'], token)
		
		alter_column(project['id'], draft, columns['id'], columns['options'][0]['id'], token)

	print("Completed populating github project!")
	
def add_issue(project_name, template, repo, pid, token):
	"""
	Create an issue and associate it with a project v2

	:param project_name: Prefix to attach to the ticket name
	:type project_name: string
	:param template: Path to the issue template that will be the body of the issue
	:type template: Path, as string
	:param repo: Github repository (e.g. QualitativeDataRepository/dvcurator-python)
	:type repo: string
	:param pid: Project ID
	:type pid: string
	:param token: Github API token
	:type token: string
	:return: ID of the newly created issue, or the API error
	:rtype: string or list[str]
	"""
	import os, json, requests, re
	
	token_header = {'Authorization': "token " + token}

	# Format issue name from template filename
	issue_name = os.path.basename(template)
	issue_name = re.sub('\.md', '', issue_name)
	issue_name = re.sub('_', ' ', issue_name)
	issue_name = issue_name.title()

	# Import the markdown file as the issue body
	f = open(template, "r")
	body = f.readlines()
	issue_url = github_api + "/repos/" + repo + "/issues"
	metadata = {'title': project_name + " - " + issue_name, 'body': ''.join(body) }
	resp = requests.post(issue_url, json.dumps(metadata), headers=token_header).json()

	if "node_id" in resp.keys():
		issue = resp['node_id']
		
		query = """
			mutation ($issue: ID!, $pid: ID!) {
				addProjectV2ItemById(input: {contentId: $issue, projectId: $pid})
				{item {id}}
			} 
			"""

		params={"issue": issue, "pid": pid}
		issue = gql_query(query, token, params)

		print("Issue added: " + issue_name)
		return issue['addProjectV2ItemById']['item']['id']
	else:
		print("issue creation went wrong with " + issue_name)
		return issue
