#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

def get_citation(host, doi, token=""):
	import requests

	if not doi.startswith("doi:"):
		print("Error: DOIs should start with \"doi:\"")
		return None
	
	# Scrape data and metadata from dataverse
	dataset_url = 'https://' + host 
	dataset_url += '/api/datasets/:persistentId/?persistentId=' + doi
	if (not token):
		dataset = requests.get(dataset_url)
	else:
		key = {'X-Dataverse-Key': token}
		dataset = requests.get(dataset_url, headers=key)
		
	if (dataset.json()['status']=="ERROR"):
		print("Error: " + dataset.json()['message'])
		return None
		
	citation=dataset.json()['data']['latestVersion']['metadataBlocks']['citation']['fields']
	fields = [] # Make an index of all the metadata fields
	values = []
	for entry in citation:
		fields.append(entry['typeName'])
		values.append(entry['value'])
	return dict(zip(fields, values)) 

def download_dataset(host, doi, folder, token=None):
	import zipfile, os, requests, urllib.request, json

	edit_path = os.path.join(folder, "QDR Prepared/1_extract")
	if not os.path.exists(edit_path):
		os.makedirs(edit_path) # Creates parents as well
		#print("Directory '%s' created" %folder_path)
	else: # If the folder already exists, don't overwrite!!
		print("Error: extract folder already exists!")
		return None

	zip_url = 'https://' + host
	zip_url += '/api/access/dataset/:persistentId/?persistentId=' + doi
	zip_url += '&format=original'
	metadata_url = "https://" + host 
	metadata_url += '/api/datasets/:persistentId/versions?persistentId=' + doi
	print("Downloading Dataverse files", end="... ")
	if token:
		key = {'X-Dataverse-Key': token}
		r = requests.get(zip_url, headers=key, allow_redirects=True, stream=True)
		metadata = requests.get(metadata_url, headers=key, allow_redirects=True)
	else:
		r = requests.get(zip_url, allow_redirects=True, stream=True)
		metadata = requests.get(metadata_url, allow_redirects=True)

	# Write metadata
	with open(os.path.join(folder, "Original metadata.json"), "w") as outfile:
		json.dump(metadata.json()['data'][0]['files'], outfile, indent=4)
	
	# Write the zip file
	zip_path = os.path.join(folder, "Original Deposit.zip")
	with open(zip_path, 'wb') as outfile:
		for chunk in r.iter_content(chunk_size = 1024):
			if(chunk):
				outfile.write(chunk)
	print("Done!")

				
	print("Extracting Dataverse files", end="... ")
	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
		zip_ref.extractall(edit_path)
	print("Done!")

	manifest = os.path.join(edit_path, 'MANIFEST.TXT')
	if (os.path.exists(manifest)):
		os.remove(manifest)
		
	return edit_path
