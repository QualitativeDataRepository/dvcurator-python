#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dvcurator.py
#  
#  Copyright 2021 Michael McCall <mimccall@syr.edu>
#

import tkinter as tk
import sys

class redirect_text(object):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, text_ctrl):
        """Constructor"""
        self.output = text_ctrl
        
    #----------------------------------------------------------------------
    def write(self, string):
        """"""
        self.output.insert(tk.END, string)

def find_config():
	from tkinter import filedialog
	file_type = (('ini file', '*.ini'),)
	config = filedialog.askopenfilename(filetypes=file_type)
	print(config)

def load_config():
	import configparser
	config = configparser.ConfigParser()
	config.read(config_file)
	
	#host = config['default']['host']
	#gh_repo = config['default']['repo']
	#dv_token = config['default']['dataverse_token']
	#gh_token = config['default']['github_token']
	#dropbox = config['default']['dropbox']
	
def which_issues():
	for issue in issues_selected:
		print(issue.get())

root=tk.Tk()
root.title("dvcurator")


# Issue checklist
checklist = tk.Frame(root)
from pkg_resources import resource_listdir
issues = resource_listdir("dvcurator", "issues/")
issues_selected = []
for n, issue in enumerate(issues):
	issues_selected.append(tk.StringVar(value=issue))
	i = tk.Checkbutton(checklist, text=issue, onvalue=issue, offvalue=None, variable=issues_selected[n])
	i.pack()

# Settings
settings = tk.Frame(root)
config_file=tk.StringVar()
config_label = tk.Label(settings, text="Load config file: ")
config_entry = tk.Button(settings, text="Select ini file", command=find_config)
config_label.grid(column=1, row=1)
config_entry.grid(column=2, row=1)

doi=tk.StringVar()
doi_label = tk.Label(settings, text="Persistent ID (DOI): ")
doi_entry = tk.Entry(settings, textvariable=doi)
doi_label.grid(column=1, row=2)
doi_entry.grid(column=2, row=2)

host = tk.StringVar()
host_label = tk.Label(settings, text="Dataverse host: ")
host_entry = tk.Entry(settings, textvariable=host)
host_label.grid(column=1, row=3)
host_entry.grid(column=2, row=3)

dv_token = tk.StringVar()
dv_label = tk.Label(settings, text="Dataverse token: ")
dv_entry = tk.Entry(settings, textvariable=dv_token)
dv_label.grid(column=1, row=4)
dv_entry.grid(column=2, row=4)

repo = tk.StringVar()
repo_label = tk.Label(settings, text="Github repository: ")
repo_entry = tk.Entry(settings, textvariable=repo)
repo_label.grid(column=1, row=5)
repo_entry.grid(column=2, row=5)

gh_token = tk.StringVar()
gh_label = tk.Label(settings, text="Github token: ")
gh_entry = tk.Entry(settings, textvariable=gh_token)
gh_label.grid(column=1, row=6)
gh_entry.grid(column=2, row=6)


settings.grid(column=1, row=1)
checklist.grid(column=2, row=1)

from tkinter import scrolledtext
out = scrolledtext.ScrolledText(root)
redir = redirect_text(out)
sys.stdout = redir
out.grid(column=1, row=3)

quit = tk.Button(root, text="Exit", command=root.quit) #command=which_issues) 
quit.grid(column=1, row=2)

root.mainloop()
