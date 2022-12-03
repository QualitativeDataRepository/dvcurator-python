# dvcurator -- Automating common Dataverse Curation tasks
[![codecov.io](https://codecov.io/gh/QualitativeDataRepository/dvcurator-python/branch/master/graphs/badge.svg?branch=master)](https://app.codecov.io/gh/QualitativeDataRepository/dvcurator-python)

The tool is based on QDR's curation practices and will likely require modifications for other repositories.

# Functionality

This program executes four main tasks:

1. Creating a local curation folder (ideally synced elsewhere, like dropbox) to edit the data, with subfolders for Original Deposit and Prepared 
2. Downloading the .zip file for the full data project to the Original Deposit folder and an unzipped version to QDR Prepared for further Curation
3. Creating github issues for standard curation tasks and associating them with a github Project for the curation of the data project.
4. Automatically setting metadata for PDF files based on Dataverse metadata

# Installing dvcurator-python

Most users will want to use the applications available in the [release section](https://github.com/QualitativeDataRepository/dvcurator-python//releases/). 

*NOTE:* Syracuse University office computers cannot run this program directly. You need to create a folder directly on the C: drive called "Apps-SU" (case sensitive). The full path to this directory should be "C:\Apps-SU". Drag and drop the `dvcurator_win.exe` file into this new folder from your downloads folder, and run it from there. 

# Running dvcurator-python

This program is operated primarily through the GUI. If you downloaded the self-contained binaries, just double-click and run.

Running the .exe file from the release page requires *no additional software*.

An .ini configuration file is used to save program settings, like the github and dataverse tokens. After entering the values into the program, you can save a .ini config file from the "File" menu at the top. 

Some functions, like downloading public datasets, will operate without API tokens, but expect potential bugs.

# Tokens

To be fully functional, the following parameters must be set:
* A **project DOI** in the form `doi:10.1234/abcdef`. Once metadata is loaded for that DOI, use the "Reset dvcurator" button to input a different DOI.  
* A **github token**
  * To create a github token, go to your github developer settings/personal access tokens at https://github.com/settings/tokens
  * Click on "Generate New Token", and select "Generate New Token (classic)"
  * Give the token a recognizable name such as "QDR Curation" and check the following boxes:
    * repo
    * admin:org 
    * project
  * Click "Generate Token" at the bottom of the screen. Make sure to note down your token and keep it safe (you won't be able to access this later)
* A **dataverse API key** -- this must be for the dataverse installation you will work with.
  * Find or create this under https://data.qdr.syr.edu/dataverseuser.xhtml?selectTab=apiTokenTab (substitute the domain if not using QDR)
 
 Both of these tokens are entered on into the main window of dvcurator, under "Github token" and "Dataverse token" respectively.

Other parameters are:
- QDR GA folder: Where the archive will be downloaded and extracted to. Usually points to a folder that syncs with Dropbox, but does not necessarily need to be. For QDR GA's this should very literally be the "QDR GA" folder within the QDR Dropbox.

## For developers (i.e. not most users!)

The more adventurous can install this package directly through pip. If you have both pip and git installed, this package can be downloaded and installed directly with:

`pip install git+https://github.com/QualitativeDataRepository/dvcurator-python`

Otherwise, this package can be installed from a zip file:

`pip install dvcurator-python-master.zip`

If you want to run `dvcurator` as an interpreted program, the python library requrirements are listed in `requirements.txt`.

### Running

Installations through pip can be run directly, e.g.

`python3 -m dvcurator`

