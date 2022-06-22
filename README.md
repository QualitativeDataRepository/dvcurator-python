# dvcurator -- Automating common Dataverse Curation tasks
[![codecov.io](https://codecov.io/gh/QualitativeDataRepository/dvcurator-python/branch/master/graphs/badge.svg?branch=master)](https://app.codecov.io/gh/QualitativeDataRepository/dvcurator-python)

The tool is based on QDR's curation practices and will likely require modifications for other repositories.

# Functionality

This program executes four main tasks:

1. Creating a local curation folder (ideally synced elsewhere, like dropbox) to edit the data, with subfolders for Original Deposit and Prepared 
2. Downloading the .zip file for the full data project to the Original Deposit folder and an unzipped version to QDR Prepared for further Curation
3. Automatically setting metadata for PDF files based on dataverse metadata
4. Creating github issues for standard curation tasks and associating them with a github Project for the curation of the data project.

# Installing dvcurator-python

Most users will want to use the applications available in the [release section](https://github.com/QualitativeDataRepository/dvcurator-python//releases/). These are self-contained binaries for Windows (.exe) annd Mac (.zip) and require no additional dependencies to run.

## For developers (i.e. not most users!)

The more adventurous can install this package directly through pip. If you have both pip and git installed, this package can be downloaded and installed directly with:

`pip install git+https://github.com/QualitativeDataRepository/dvcurator-python`

Otherwise, this package can be installed from a zip file:

`pip install dvcurator-python-master.zip`


# Running dvcurator-python

This program is operated primarily through the GUI. If you downloaded the self-contained binaries, just double-click and run.

## For developers

Installations through pip can be run directly, e.g.

`python3 -m dvcurator`

# Requirements

Running the self-contained binaries from the release page requires *no additional software*.

If you want to run `dvcurator` as an interpreted program, the python library requrirements are listed in `requirements.txt`.

An .ini file is used to configure program parameters. The included file `config.ini.default` can be used as a template, or one can be created and saved in the program itself. Some functions, like downloading public datasets, will operate without keys, but expect potential bugs.

To be fully functional, the following parameters must be set:
* A **project DOI** in the form `doi:10.1234/abcdef`. Once metadata is loaded for that DOI, use the "Reset dvcurator" button to input a different DOI.  
* A **github token**
  * To create a github token, go to your github developer settings/personal access tokens at https://github.com/settings/tokens
  * Click on "Generate New Token"
  * Give the token a recognizable name such as "QDR Curation" and check the following boxes:
    * repo
    * admin:org 
    * notifications
    * write:discussion
  * Click "Generate Token" at the bottom of the screen. Make sure to note down your token and keep it safe (you won't be able to access this later)
* A **dataverse API key** -- this must be for the dataverse installation you will work with.
  * Find or create this under https://data.qdr.syr.edu/dataverseuser.xhtml?selectTab=apiTokenTab (substitute the domain if not using QDR)

Other parameters are:
- Dropbox folder: Where the archive will be downloaded and extracted to. Usually points to a folder that syncs with Dropbox, but does not necessarily need to be.
- Repo: Which github repository to post the issues. This should be provided without the domain, i.e. `QualitativeDataRepository/Project-Curation`
- Host: Where the dataverse instance is hosted (For QDR: `data.qdr.syr.edu`)
