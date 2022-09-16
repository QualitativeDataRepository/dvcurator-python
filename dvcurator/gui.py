#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

import tkinter as tk
import sys, threading
from tkinter.messagebox import showwarning
import dvcurator.github, dvcurator.dataverse, dvcurator.rename, dvcurator.convert, dvcurator.fs, dvcurator.pdf_metadata, dvcurator.version

class redirect_text(object):
	def __init__(self, text_ctrl):
		self.output = text_ctrl        
	def write(self, string):
		self.output.insert(tk.END, string)
		self.output.see(tk.END)
	def flush(self):
		pass

class MainApp(tk.Frame):
	def disable_buttons(self):
		self.cite_button.config(state="disabled")
		self.download_button.config(state="disabled")
		self.makeproject_button.config(state="disabled")
		self.menubar.entryconfig("Edit", state=tk.DISABLED)
		self.reset_button.config(state="disabled")

	def enable_buttons(self):
		self.cite_button.config(state="normal")
		self.download_button.config(state="normal")
		self.makeproject_button.config(state="normal")
		self.menubar.entryconfig("Edit", state=tk.NORMAL)
		self.reset_button.config(state="normal")

	def schedule_check(self, t):
		self.after(1000, self.check_if_done, t)
	
	def check_if_done(self, t):
		if not t.is_alive():
			self.enable_buttons()
		else:
			self.schedule_check(t)

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
			test = dvcurator.fs.check_dropbox(dropbox)
			if not test:
				return
			self.dropbox_entry.config(text=os.path.split(self.dropbox.get())[1])
			print("Dropbox folder: " + self.dropbox.get())

	def set_subfolder(self):
		from tkinter import filedialog
		import os.path
		subfolder = filedialog.askdirectory()
		if not subfolder:
			return
		self.subfolder_path = subfolder
		print("Subfolder set to: " + self.subfolder_path)

	# Open project directory
	def open_explorer(self):
		import os
		if not self.subfolder_path:
			print("Error: No subfolder specified")
			return
		elif not os.path.exists(self.subfolder_path):
			print("Error: subfolder does not exist: " + self.subfolder_path)
			return

		os.startfile(os.path.realpath(self.subfolder_path))
		
	def load_citation(self):
		import os.path
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
		# self.project_name = project_name(self.citation['depositor'].split(', ')[0], self.citation['title'])
		self.project_name = dvcurator.rename.project_name(self.citation['author'][0]['authorName']['value'].split(', ')[0], self.citation['title'])
		print("Loaded: " + self.project_name)

		self.subfolder_path = dvcurator.fs.check_dropbox(self.dropbox.get(), self.project_name)
		if not self.subfolder_path:
			self.subfolder_path = os.path.join(self.dropbox.get(),  'QDR Project - ' + self.project_name)
			print("You need to download/extract or manually specify a subfolder.")
		if os.path.exists(self.subfolder_path):
			print("Existing extracted project detected at: " + self.subfolder_path)
		
		# Enable the next step buttons
		self.doi_entry.config(state="disabled")
		self.download_button.config(state="normal")
		self.makeproject_button.config(state="normal")
		self.menubar.entryconfig("Edit", state=tk.NORMAL)

	def download_extract(self):
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.dataverse.download_dataset, args=(self.host.get(), self.doi.get(), self.subfolder_path, self.dv_token.get()))
		t.start()
		self.schedule_check(t)

	def make_github(self):
		if (not self.gh_token.get()):
			print("Error: no github token specified")
			return
		if (not self.repo.get()):
			print("Error: no github repository specified")
			return

		# Create github project + issues
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.github.generate_template, 
			args=(self.doi.get(), self.citation, self.project_name, self.repo.get(), self.gh_token.get(), self.issues_selected))
		t.start()
		self.schedule_check(t)

	def rename(self):
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.rename.basic_rename, args=(self.subfolder_path, self.citation))
		t.start()
		self.schedule_check(t)
	
	def convert(self):		
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.convert.docx_pdf, args=(self.subfolder_path, None))
		t.start()
		self.schedule_check(t)

	def set_metadata(self):
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.pdf_metadata.standard_metadata, args=(self.subfolder_path, self.citation))
		t.start()
		self.schedule_check(t)

	def reset_all(self):
		# Reset DOI entry
		self.doi.set("")
		self.doi_entry.config(state="normal")
		# Disable all other buttons
		self.download_button.config(state="disabled")
		self.makeproject_button.config(state="disabled")
		self.menubar.entryconfig("Edit", state=tk.DISABLED)
		self.out.delete('1.0', tk.END)

	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, args, **kwargs)
		self.parent = parent
		
		# Start with the menu
		self.menubar = tk.Menu(self)

		self.filemenu = tk.Menu(self.menubar, tearoff=False)
		self.filemenu.add_command(label="Open config", command=self.load_config)
		self.filemenu.add_command(label="Save current config", command=self.save_config)
		self.filemenu.add_command(label="Exit dvcurator", command=parent.destroy)
		self.menubar.add_cascade(label="File", menu=self.filemenu)

		self.editmenu = tk.Menu(self.menubar, tearoff=False)
		self.editmenu.add_command(label="Basic file rename", command=self.rename)
		self.editmenu.add_command(label="Convert docx to pdf", command=self.convert)
		self.editmenu.add_command(label="Set PDF metadata", command=self.set_metadata)
		self.editmenu.add_separator()
		self.editmenu.add_command(label="Open Dropbox subfolder", command=self.open_explorer)
		self.editmenu.add_command(label="Select project subfolder manually", command=self.set_subfolder)
		self.menubar.add_cascade(label="Edit", menu=self.editmenu)
		self.menubar.entryconfig("Edit", state=tk.DISABLED)
		parent.config(menu=self.menubar)

		# Checklist of tickets included in the .md files
		checklist = tk.LabelFrame(self, text="Project issues:")
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

		self.reset_button = tk.Button(process, text="Reset dvcurator", command=self.reset_all)
		self.reset_button.pack()
		
		settings.grid(column=1, row=1)
		checklist.grid(column=2, row=2, padx=10)
		process.grid(column=2, row=1)

		from tkinter import scrolledtext
		self.out = scrolledtext.ScrolledText(self, width=40, height=20)
		redir = redirect_text(self.out)
		sys.stdout = redir
		sys.stderr = redir
		self.out.grid(column=1, row=2)

		is_latest = dvcurator.github.check_version(dvcurator.version.version, "QualitativeDataRepository/dvcurator-python")
		#if not is_latest:
		#	tk.messagebox.showwarning(title="Get new version", message="Please download new version of dvcurator")


def main():
	root=tk.Tk()
	root.title("dvcurator " + dvcurator.version.version)
	MainApp(root).pack(side="top", fill="both", expand=True)
	root.mainloop()

if __name__ == "__main__":
	main()
