#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

import tkinter as tk
import sys
import dvcurator.github, dvcurator.dataverse, dvcurator.rename, dvcurator.convert, dvcurator.pdf_metadata, dvcurator.version

# This is the function to make the folder name from the Dataverse project name.
# Since we use this multiple times
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
		import os.path
		file_type = (('ini file', '*.ini'),('All files', '*.*'),)
		config_file = filedialog.askopenfilename(filetypes=file_type)
		if config_file:
			import configparser
			config = configparser.ConfigParser()
			config.read(config_file)
			self.host.set(config['default']['host'])
			self.repo.set(config['default']['repo'])
			self.dv_token.set(config['default']['dataverse_token'])
			self.gh_token.set(config['default']['github_token'])
			self.dropbox.set(config['default']['dropbox'])
			self.dropbox_entry.config(text=os.path.split(self.dropbox.get())[1])
			print("Loaded: " + config_file)

	# function to save settings as .ini file
	def save_config(self):
		from tkinter.filedialog import asksaveasfilename
		file_type = (('ini file', '*.ini'),('All files', '*.*'),)
		f = asksaveasfilename(filetypes=file_type)
		if f:
			import configparser
			config = configparser.ConfigParser()
			config['default'] = {"host": self.host.get(),
								"repo": self.repo.get(),
								"dataverse_token": self.dv_token.get(),
								"github_token": self.gh_token.get(),
							"dropbox": self.dropbox.get()}
			with open(f, 'w') as config_file:
				config.write(config_file)
			print("Written: " + f)
			
	# Set dropbox directory path, open OS folder select dialog
	def set_dropbox(self):
		from tkinter import filedialog
		import os.path
		dropbox = filedialog.askdirectory()
		if (dropbox):
			self.dropbox.set(dropbox)
			self.dropbox_entry.config(text=os.path.split(self.dropbox.get())[1])
			print("Dropbox folder: " + self.dropbox.get())
		
	def load_citation(self):
		if (not self.doi.get()):
			print("Error: No persistent ID specified")
			return
		if (not self.host.get()):
			print("Error: No dataverse host specified")
			return
			
		self.citation = dvcurator.dataverse.get_citation(self.host.get(), self.doi.get(), self.dv_token.get())
		if (not self.citation):
			return
			
		# citation['depositor'].split(', ')[0] is the last name of the depositor
		# self.folder_name = project_name(self.citation['depositor'].split(', ')[0], self.citation['title'])
		self.folder_name = project_name(self.citation['author'][0]['authorName']['value'].split(', ')[0], self.citation['title'])
		special_characters = ['!','#','$','%', '&','@','[',']',']','_',':',';',"'"]
		for i in special_characters:
			self.folder_name = self.folder_name.replace(i,'')
			
		print(self.folder_name)
		
		# Enable the next step buttons
		self.doi_entry.config(state="disabled")
		self.download_button.config(state="normal")
		self.makeproject_button.config(state="normal")
		self.convert_button.config(state="normal")
		self.rename_button.config(state="normal")
		self.pdfmetadata_button.config(state="normal")

	def download_extract(self):
		extracted_path = dvcurator.dataverse.download_dataset(self.host.get(), self.doi.get(), self.dv_token.get(), self.folder_name, self.dropbox.get())
		if not extracted_path:
			print("Error: folder may already exist")
		else:
			print("Extracted to: " + extracted_path)

	def make_github(self):
		from pkg_resources import resource_filename
		import os.path
		
		if (not self.gh_token.get()):
			print("Error: no github token specified")
			return
		if (not self.repo.get()):
			print("Error: no github repository specified")
			return
			
		if (not dvcurator.github.check_repo(self.repo.get(), self.gh_token.get())):
			print("Error: github repository doesn't exist")
			return
			
		existing = dvcurator.github.search_existing(self.folder_name, self.repo.get(), self.gh_token.get())
		if (existing):
			print("Error: existing github issues!!")
			return

		# Create github project + issues
		self.project = dvcurator.github.create_project(self.doi.get(), self.citation, self.folder_name, self.repo.get(), self.gh_token.get())
		print("Created project: " + self.folder_name)
		# Get internal issue templates from selected checkboxes
		for issue in self.issues_selected:
			path = issue.get()
			if (path != "0"):
				if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
					path = os.path.join(sys._MEIPASS, "issues", path)
				else:
					path = resource_filename("dvcurator", "issues/" + path)
				dvcurator.github.add_issue(self.folder_name, path, self.repo.get(), self.project, self.gh_token.get())
				print(issue.get() + " added to project")

	def rename(self):		
		import os.path 
		if (os.path.isdir(self.dropbox.get())):
			last_name = self.citation['author'][0]['authorName']['value'].split(", ")[0]
			new_path = dvcurator.rename.basic_rename(self.dropbox.get(), self.folder_name, last_name)
			print("Files renamed in: " + new_path)
		else:
			print("Error: Dropbox folder invalid")
	
	def convert(self):		
		new_path = dvcurator.rename.copy_new_step(self.dropbox.get(), self.folder_name, "convert-pdf")
		dvcurator.convert.docx_pdf(new_path)
		print("Files converted to: " + new_path)

	def set_metadata(self):
		import os.path 
		if (os.path.isdir(self.dropbox.get())):
			metadata_path = dvcurator.pdf_metadata.make_metadata_folder(self.dropbox.get(), self.folder_name)
			if (not metadata_path): # Errors are outputted by pdf_metadata
				return
			dvcurator.pdf_metadata.standard_metadata(metadata_path, self.citation['author'][0]['authorName']['value'])
			print("PDF metadata updated in new folder")
		else:
			print("Error: Dropbox folder invalid")

	def reset_all(self):
		self.doi.set("")
		self.doi_entry.config(state="normal")
		self.download_button.config(state="disabled")
		self.makeproject_button.config(state="disabled")
		self.convert_button.config(state="disabled")
		self.rename_button.config(state="disabled")
		self.pdfmetadata_button.config(state="disabled")
		self.out.delete('1.0', tk.END)
	
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, args, **kwargs)
		self.parent = parent

		checklist = tk.Frame(self)
		if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
				self.issues = os.listdir(os.path.join(sys._MEIPASS, "issues"))
		else:
			from pkg_resources import resource_listdir
			self.issues = resource_listdir(__name__, "issues/")

		self.issues_selected = []
		for n, issue in enumerate(self.issues):
			self.issues_selected.append(tk.StringVar(value=issue))
			i = tk.Checkbutton(checklist, text=issue, onvalue=issue, offvalue=None, variable=self.issues_selected[n])
			i.pack()
		
		# Settings
		settings = tk.Frame(self)
		config_file=tk.StringVar()
		config_label = tk.Label(settings, text="Config file: ")
		config_options = tk.Frame(settings)
		config_entry = tk.Button(config_options, text="Open", command=self.load_config)
		config_save = tk.Button(config_options, text="Save", command=self.save_config)

		config_label.grid(column=1, row=1)
		config_entry.grid(column=1, row=1)
		config_save.grid(column=2, row=1)
		config_options.grid(column=2, row=1)
		
		self.doi=tk.StringVar()
		doi_label = tk.Label(settings, text="Persistent ID (DOI): ")
		self.doi_entry = tk.Entry(settings, textvariable=self.doi)
		doi_label.grid(column=1, row=2)
		self.doi_entry.grid(column=2, row=2)
		
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
		self.dropbox_entry = tk.Button(settings, text="Select folder", command=self.set_dropbox)
		dropbox_label.grid(column=1, row=7)
		self.dropbox_entry.grid(column=2, row=7)
		
		process = tk.Frame(self)
		self.cite_button = tk.Button(process, text="Load metadata", command=self.load_citation)
		self.cite_button.pack()
		self.download_button = tk.Button(process, text="Download and extract", state="disabled", command=self.download_extract)
		self.download_button.pack()
		self.makeproject_button = tk.Button(process, text="Make github project", state="disabled", command=self.make_github)
		self.makeproject_button.pack()

		#fileprocess_options = ["Basic rename", "Convert docx to PDF"]
		#fileprocess_var = tk.StringVar()
		#fileprocess_var.set(fileprocess_options[0])

		#self.fileprocess_menu = tk.OptionMenu(process, fileprocess_var, *fileprocess_options)
		#self.fileprocess_menu.pack(expand=True)

		self.convert_button = tk.Button(process, state="disabled", text="Convert docx to PDF", command=self.convert)
		self.convert_button.pack()

		self.rename_button = tk.Button(process, state="disabled", text="Basic rename", command=self.rename)
		self.rename_button.pack()

		self.pdfmetadata_button = tk.Button(process, state="disabled", text="Set metadata in PDF files", command=self.set_metadata)
		self.pdfmetadata_button.pack()

		reset_button = tk.Button(process, text="Reset dvcurator", command=self.reset_all)
		reset_button.pack()
		
		settings.grid(column=1, row=1)
		checklist.grid(column=2, row=2)
		process.grid(column=2, row=1)
		
		from tkinter import scrolledtext
		self.out = scrolledtext.ScrolledText(self, width=40, height=20)
		redir = redirect_text(self.out)
		sys.stdout = redir
		sys.stderr = redir
		self.out.grid(column=1, row=2)

def main():
	root=tk.Tk()
	root.title("dvcurator " + dvcurator.version.version)
	MainApp(root).pack(side="top", fill="both", expand=True)
	root.mainloop()

if __name__ == "__main__":
	main()
