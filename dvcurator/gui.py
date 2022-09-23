#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

import tkinter as tk
import sys, threading, os
import dvcurator.github, dvcurator.dataverse, dvcurator.rename, dvcurator.readme, dvcurator.convert, dvcurator.fs, dvcurator.pdf, dvcurator.version

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
		self.out.delete('1.0', tk.END)
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

	# File menu buttons
	def open_config(self):
		from tkinter import filedialog
		file_type = (('ini file', '*.ini'),('All files', '*.*'),)
		config_file = filedialog.askopenfilename(filetypes=file_type)
		if (os.path.exists(config_file)):
			self.load_config(config_file)
		
	def load_config(self, path=None):
		if not os.path.exists(path):
			return None
		import configparser
		config = configparser.ConfigParser()
		config.read(path)
		self.dv_token.set(config['default']['dataverse_token'])
		self.gh_token.set(config['default']['github_token'])
		self.dropbox.set(config['default']['dropbox'])
		self.dropbox_entry.config(text=os.path.split(self.dropbox.get())[1])
		print("Loaded settings: " + path)

	# function to save settings as .ini file
	def save_config_as(self):
		from tkinter.filedialog import asksaveasfilename
		file_type = (('ini file', '*.ini'),('All files', '*.*'),)
		f = asksaveasfilename(filetypes=file_type)
		if f:
			self.save_config(f)

	def save_config(self, path=None):
		path = self.local_ini if not path else path
		import configparser
		config = configparser.ConfigParser()
		config['default'] = {"dataverse_token": self.dv_token.get(),
							"github_token": self.gh_token.get(),
						"dropbox": self.dropbox.get()}
		with open(path, 'w') as config_file:
			config.write(config_file)
		print("Written: " + path)

	# Set dropbox directory path, open OS folder select dialog
	def check_subfolder(self):
		self.subfolder_path = dvcurator.fs.check_dropbox(self.dropbox.get(), self.project_name)
		if not self.subfolder_path:
			self.subfolder_path = os.path.join(self.dropbox.get(),  'QDR Project - ' + self.project_name)
			print("You need to download/extract or manually specify a subfolder.")
		if os.path.exists(self.subfolder_path):
			print("Existing extracted project detected at: " + self.subfolder_path)

	def set_dropbox(self):
		from tkinter import filedialog
		dropbox = filedialog.askdirectory()
		if not dropbox:
			return None

		self.dropbox.set(dropbox)
		test = dvcurator.fs.check_dropbox(dropbox)
		if not test:
			return
		self.dropbox_entry.config(text=os.path.split(self.dropbox.get())[1])
		print("Dropbox folder: " + self.dropbox.get())
		if hasattr(self, "metadata"):
			self.check_subfolder()

	def set_subfolder(self):
		from tkinter import filedialog
		subfolder = filedialog.askdirectory()
		if not subfolder:
			return
		self.subfolder_path = subfolder
		print("Subfolder set to: " + self.subfolder_path)

	# Open project directory (edit menu)
	def open_explorer(self):
		if not self.subfolder_path:
			print("Error: No subfolder specified")
			return
		elif not os.path.exists(self.subfolder_path):
			print("Error: subfolder does not exist: " + self.subfolder_path)
			return

		# Windows, Mac and Linux require different handlers
		if sys.platform == "win32":
			os.startfile(self.subfolder_path)
		else:
			import subprocess
			opener = "open" if sys.platform == "darwin" else "xdg-open"
			subprocess.call([opener, self.subfolder_path])

	# Main window buttons
	def load_citation(self):
		if (not self.doi.get()):
			print("Error: No persistent ID specified")
			return
		if not dvcurator.fs.check_dropbox(self.dropbox.get()):
			print("Error: Set valid Dropbox folder first")
			return
		# Grab the citation
		self.metadata = dvcurator.dataverse.get_metadata(self.doi.get(), self.dv_token.get())
		if (not self.metadata):
			print("Error: citation failed to load.")
			return
		self.citation = dvcurator.dataverse.get_citation(self.metadata)
		self.project_name = dvcurator.rename.project_name(self.citation)
		print("Loaded: " + self.project_name)

		self.check_subfolder()

		# Enable the next step buttons
		self.doi_entry.config(state="disabled")
		self.download_button.config(state="normal")
		self.makeproject_button.config(state="normal")
		self.menubar.entryconfig("Edit", state=tk.NORMAL)

	def download_extract(self):
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.dataverse.download_dataset, 
			args=(self.metadata, self.subfolder_path, self.dv_token.get()))
		t.start()
		self.schedule_check(t)

	def make_github(self):
		if (not self.gh_token.get()):
			print("Error: no github token specified")
			return

		# Create github project + issues
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.github.generate_template, 
			args=(self.metadata, self.project_name, self.gh_token.get()))
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

	# Edit menu options
	def rename(self):
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.rename.basic_rename, 
			args=(self.subfolder_path, self.citation))
		t.start()
		self.schedule_check(t)
	
	def convert(self):
		import pythoncom	
		pythoncom.CoInitialize()
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.convert.docx_pdf, 
			args=(self.subfolder_path, None))
		t.start()
		self.schedule_check(t)

	def set_metadata(self):
		self.disable_buttons()
		t = threading.Thread(target=dvcurator.pdf.standard_metadata, 
			args=(self.subfolder_path, self.citation))
		t.start()
		self.schedule_check(t)

	def create_readme(self):
		if (not self.dv_token.get()):
			print("Error: no dataverse token specified")
			return

		self.disable_buttons()
		t = threading.Thread(target=dvcurator.readme.generate_readme, 
			args=(self.metadata, os.path.join(self.subfolder_path, "QDR Prepared"), self.dv_token.get()))
		t.start()
		self.schedule_check(t)

	def close_window(self):
		self.save_config()
		self.parent.destroy()

	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, args, **kwargs)
		self.parent = parent
		
		# Start with the menu
		self.menubar = tk.Menu(self)

		self.filemenu = tk.Menu(self.menubar, tearoff=False)
		self.filemenu.add_command(label="Save config", command=self.save_config)
		self.filemenu.add_command(label="Save config As", command=self.save_config_as)
		self.filemenu.add_command(label="Open config", command=self.open_config)
		self.filemenu.add_command(label="Exit dvcurator", command=parent.destroy)
		self.menubar.add_cascade(label="File", menu=self.filemenu)

		self.editmenu = tk.Menu(self.menubar, tearoff=False)
		self.editmenu.add_command(label="Basic file rename", command=self.rename)
		self.editmenu.add_command(label="Convert docx to pdf", command=self.convert)
		self.editmenu.add_command(label="Set PDF metadata", command=self.set_metadata)
		self.editmenu.add_command(label="Generate README", command=self.create_readme)
		self.editmenu.add_separator()
		self.editmenu.add_command(label="Open Dropbox subfolder", command=self.open_explorer)
		self.editmenu.add_command(label="Select project subfolder manually", command=self.set_subfolder)
		self.menubar.add_cascade(label="Edit", menu=self.editmenu)
		self.menubar.entryconfig("Edit", state=tk.DISABLED)
		parent.config(menu=self.menubar)

		# Checklist of tickets included in the .md files
		#checklist = tk.LabelFrame(self, text="Project issues:")
		#self.issues_selected = []
		#for n, issue in enumerate(self.issues):
		#	self.issues_selected.append(tk.StringVar(value=issue))
		#	i = tk.Checkbutton(checklist, text=issue, onvalue=issue, offvalue=None, variable=self.issues_selected[n])
		#	i.pack()
		
		# Settings
		settings = tk.Frame(self)

		self.doi=tk.StringVar()
		doi_label = tk.Label(settings, text="Persistent ID (DOI): ")
		self.doi_entry = tk.Entry(settings, textvariable=self.doi)
		doi_label.grid(column=1, row=2)
		self.doi_entry.grid(column=2, row=2)
			
		self.dv_token = tk.StringVar()
		dv_label = tk.Label(settings, text="Dataverse token: ")
		dv_entry = tk.Entry(settings, textvariable=self.dv_token)
		dv_label.grid(column=1, row=4)
		dv_entry.grid(column=2, row=4)
			
		self.gh_token = tk.StringVar()
		gh_label = tk.Label(settings, text="Github token: ")
		gh_entry = tk.Entry(settings, textvariable=self.gh_token)
		gh_label.grid(column=1, row=6)
		gh_entry.grid(column=2, row=6)
		
		self.dropbox=tk.StringVar()
		dropbox_label = tk.Label(settings, text="Dropbox folder: ")
		self.dropbox_entry = tk.Button(settings, width=15, text="Select folder", command=self.set_dropbox)
		dropbox_label.grid(column=1, row=7)
		self.dropbox_entry.grid(column=2, row=7, sticky="w")
		
		process = tk.Frame(self)
		pb_width = 17
		self.cite_button = tk.Button(process, width=pb_width, text="(Re)load metadata", command=self.load_citation)
		self.cite_button.grid(row=1, column=1, sticky="e")
		self.download_button = tk.Button(process, width=pb_width, text="Download and Extract", state="disabled", command=self.download_extract)
		self.download_button.grid(row=2, column=1, sticky="e")
		self.makeproject_button = tk.Button(process, width=pb_width, text="Make github project", state="disabled", command=self.make_github)
		self.makeproject_button.grid(row=3, column=1, sticky="e")

		self.reset_button = tk.Button(process, width=pb_width, text="Reset dvcurator", command=self.reset_all)
		self.reset_button.grid(row=4, column=1, sticky="e")
		
		settings.grid(column=1, row=1, padx=3, pady=3)
		process.grid(column=2, row=1, padx=3, pady=3)

		from tkinter import scrolledtext
		self.out = scrolledtext.ScrolledText(self, width=40, height=20)
		redir = redirect_text(self.out)
		sys.stdout = redir
		sys.stderr = redir
		self.out.grid(column=1, row=2, columnspan=2)

		dvcurator.github.check_version()
		self.local_ini = os.path.join(os.getcwd(), "dvcurator.ini")
		if os.path.exists(self.local_ini):
			self.load_config(self.local_ini)

		# save config on exit
		parent.protocol("WM_DELETE_WINDOW", self.close_window)


def main():
	root=tk.Tk()
	root.resizable(width=False, height=False)
	root.title("dvcurator " + dvcurator.version.version)
	MainApp(root).pack(side="top", fill="both", expand=True)
	root.mainloop()

if __name__ == "__main__":
	main()
