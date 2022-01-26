#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

import tkinter as tk
import sys

def project_name(last_name, title):
	import re
	title = re.sub("Data for: ", '', title)
	title = re.sub("(Replication )?[Dd]ata for ", '', title)
	title = re.match("^(.+?\\s){1,5}", title).group(0).rstrip()
	title = re.sub("^[^a-zA-Z]?", "", title) # get rid of any beginning non-letter chars
	title = re.sub(":.+", '', title)
	folder_name = last_name + " - " + title
	return folder_name

class redirect_text(object):
	def __init__(self, text_ctrl):
		self.output = text_ctrl        
	def write(self, string):
		self.output.insert(tk.END, string)
	def flush(self):
		pass

class MainApp(tk.Frame):
	def load_config(self):
		from tkinter import filedialog
		file_type = (('ini file', '*.ini'),)
		config_file = filedialog.askopenfilename(filetypes=file_type)
		import configparser
		config = configparser.ConfigParser()
		config.read(config_file)
		self.host.set(config['default']['host'])
		self.repo.set(config['default']['repo'])
		self.dv_token.set(config['default']['dataverse_token'])
		self.gh_token.set(config['default']['github_token'])
		self.dropbox.set(config['default']['dropbox'])
		print("Loaded: " + config_file)
		
	def load_citation(self):
		import dataverse
		self.citation = dataverse.get_citation(self.host.get(), self.doi.get(), self.dv_token.get())
		# citation['depositor'].split(', ')[0] is the last name of the depositor
		self.folder_name = project_name(self.citation['depositor'].split(', ')[0], self.citation['title'])
		print(self.folder_name)
		print("Dataverse project metadata loaded")

	def download_extract(self):
		import dataverse
		self.path = dataverse.download_dataset(self.host.get(), self.doi.get(), self.dv_token.get(), self.folder_name, self.dropbox.get())
		print("Extracted to: " + self.path)

	def make_github(self):
		import github
		existing = github.search_existing(self.folder_name, self.repo.get(), self.gh_token.get())
		if (existing):
			print("Error: existing github issues!!")
			return

		for issue in self.issues_selected:
			print(issue)

		return

		from pkg_resources import resource_filename
		# Create github project + issues
		self.project = github.create_project(self.doi.get(), self.citation, self.folder_name, self.repo.get(), self.gh_token.get())
		# Get internal issue templates from selected checkboxes
		for issue in self.issues_selected:
			if (issue):
				issue = resource_filename("dvcurator", "issues/" + issue)
				github.add_issue(self.folder_name, issue, self.repo.get(), self.project, self.gh_token.get())
	
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, args, **kwargs)
		self.parent = parent

		checklist = tk.Frame(self)
		from pkg_resources import resource_listdir
		issues = resource_listdir("dvcurator", "issues/")
		self.issues_selected = []
		for n, issue in enumerate(issues):
			self.issues_selected.append(tk.StringVar(value=issue))
			i = tk.Checkbutton(checklist, text=issue, onvalue=issue, offvalue=None, variable=self.issues_selected[n])
			i.pack()
		
		# Settings
		settings = tk.Frame(self)
		config_file=tk.StringVar()
		config_label = tk.Label(settings, text="Load config file: ")
		config_entry = tk.Button(settings, text="Select ini file", command=self.load_config)
		config_label.grid(column=1, row=1)
		config_entry.grid(column=2, row=1)
		
		self.doi=tk.StringVar()
		doi_label = tk.Label(settings, text="Persistent ID (DOI): ")
		doi_entry = tk.Entry(settings, textvariable=self.doi)
		doi_label.grid(column=1, row=2)
		doi_entry.grid(column=2, row=2)
		
		self.host = tk.StringVar()
		host_label = tk.Label(settings, text="Dataverse host: ")
		host_entry = tk.Entry(settings, textvariable=self.host)
		host_label.grid(column=1, row=3)
		host_entry.grid(column=2, row=3)
		
		self.dv_token = tk.StringVar()
		dv_label = tk.Label(settings, text="Dataverse token: ")
		dv_entry = tk.Entry(settings, textvariable=self.dv_token)
		dv_label.grid(column=1, row=4)
		dv_entry.grid(column=2, row=4)
		
		self.repo = tk.StringVar()
		repo_label = tk.Label(settings, text="Github repository: ")
		repo_entry = tk.Entry(settings, textvariable=self.repo)
		repo_label.grid(column=1, row=5)
		repo_entry.grid(column=2, row=5)
		
		self.gh_token = tk.StringVar()
		gh_label = tk.Label(settings, text="Github token: ")
		gh_entry = tk.Entry(settings, textvariable=self.gh_token)
		gh_label.grid(column=1, row=6)
		gh_entry.grid(column=2, row=6)
		
		self.dropbox=tk.StringVar()
		dropbox_label = tk.Label(settings, text="Dropbox folder: ")
		dropbox_entry = tk.Button(settings, text="Select folder")
		dropbox_label.grid(column=1, row=7)
		dropbox_entry.grid(column=2, row=7)
		
		process = tk.Frame(self)
		cite_button = tk.Button(process, text="Load metadata", command=self.load_citation)
		cite_button.pack()
		download_button = tk.Button(process, text="Download and extract", command=self.download_extract)
		download_button.pack()
		pdfmetadata_button = tk.Button(process, text="Set metadata in PDF files")
		pdfmetadata_button.pack()
		makeproject_button = tk.Button(process, text="Make github project", command=self.make_github)
		makeproject_button.pack()
		reset_button = tk.Button(process, text="Reset dvcurator")
		reset_button.pack()
		
		settings.grid(column=1, row=1)
		checklist.grid(column=2, row=2)
		process.grid(column=2, row=1)
		
		from tkinter import scrolledtext
		out = scrolledtext.ScrolledText(self, width=40, height=20)
		redir = redirect_text(out)
		sys.stdout = redir
		out.grid(column=1, row=2)

def main():
	root=tk.Tk()
	root.title("dvcurator")
	MainApp(root).pack(side="top", fill="both", expand=True)
	root.mainloop()

if __name__ == "__main__":
	main()
