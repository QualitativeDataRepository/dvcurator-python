#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def get_metadata(doi, token="", host=None):
	import requests, dvcurator.hosts

	doi = doi.strip()
	if not doi.startswith("doi:"):
		print("Error: DOIs should start with \"doi:\"")
		return None
	
	# Scrape data and metadata from dataverse
	host = dvcurator.hosts.qdr_dataverse if not host else host 
	dataset_url = host + '/api/datasets/:persistentId/?persistentId=' + doi
	if (not token):
		dataset = requests.get(dataset_url)
	else:
		key = {'X-Dataverse-Key': token}
		dataset = requests.get(dataset_url, headers=key)
	
	try: 
		dataset = dataset.json()
	except:
		print("Error: " + host + " not serving JSON")
		return None

	if (dataset['status']=="ERROR"):
		print("Error: " + dataset['message'])
		return None
	
	return(dataset)

# extract and format the citation metadata block
def get_citation(metadata):
	#metadata = get_metadata(doi, token, host)
	citation=metadata['data']['latestVersion']['metadataBlocks']['citation']['fields']
	fields = [] # Make an index of all the metadata fields
	values = []
	for entry in citation:
		fields.append(entry['typeName'])
		values.append(entry['value'])
	return dict(zip(fields, values)) 

# This pulls the "recommended citation" field
# Gotta pull from the SWORD API, not available from native metadata
def get_biblio_citation(doi, token, host=None):
	import requests, dvcurator.hosts
	import xml.etree.ElementTree as et

	doi = doi.strip()
	if not doi.startswith("doi:"):
		print("Error: DOIs should start with \"doi:\"")
		return None

	host = dvcurator.hosts.qdr_dataverse if not host else host 

	atom_url = host + "/dvn/api/data-deposit/v1.1/swordv2/edit/study/" + doi
	atom = requests.get(atom_url, auth=requests.auth.HTTPBasicAuth(token, ""))
	if atom.status_code == 400:
		return None

	tree = et.fromstring(atom.text)
	return tree[0].text

def download_dataset(doi, folder, metadata, token=None, host=None):
	import zipfile, os, urllib, json, requests, dvcurator.hosts

	doi = doi.strip()

	edit_path = os.path.normpath(os.path.join(folder, "QDR Prepared/1_extract"))
	if not os.path.isdir(edit_path):
		os.makedirs(edit_path) # Creates parents as well
		#print("Directory '%s' created" %folder_path)
	else: # If the folder already exists, don't overwrite!!
		print("Error: extract folder already exists!")
		return None

	# Write metadata
	with open(os.path.join(folder, "Original metadata.json"), "w") as outfile:
		json.dump(metadata['data']['latestVersion']['files'], outfile, indent=4)

	# Write the zip file
	zip_url = dvcurator.hosts.qdr_dataverse if not host else host 
	zip_url += '/api/access/dataset/:persistentId/?persistentId=' + doi
	zip_url += '&format=original'
	print("Downloading Dataverse files", end="... ")
	zip_path = os.path.join(folder, "Original Deposit.zip")
	opener = urllib.request.build_opener()
	if token:
		opener.addheaders = [('X-Dataverse-Key', token)]
	urllib.request.install_opener(opener)
	urllib.request.urlretrieve(zip_url, zip_path)
	print("Done!")
				
	print("Extracting Dataverse files", end="... ")
	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		zip_ref.extractall(edit_path)
	print("Done!")

	manifest = os.path.join(edit_path, 'MANIFEST.TXT')
	if (os.path.exists(manifest)):
		os.remove(manifest)
		
	return edit_path
