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

Most users will want to use the applications available in the [release section](https://github.com/QualitativeDataRepository/dvcurator-python//releases/). The release gets built by pushing to a new tag.

*NOTE:* Syracuse University office computers cannot run this program directly. You should download the [SU Lab Install.bat](https://github.com/QualitativeDataRepository/dvcurator-python/blob/master/SU%20Lab%20Install.bat) file (right click "Raw" and the top and Save Link As), and run that instead. This will install the program properly and create a shortcut on your desktop.

# Running dvcurator-python

This program is operated primarily through the GUI. If you downloaded the self-contained binaries, just double-click and run.

Running the .exe file from the release page requires *no additional software*.

An .ini configuration file is used to save program settings, like the github and dataverse tokens. After entering the values into the program, you can save a .ini config file from the "File" menu at the top. 

Some functions, like downloading public datasets, will operate without API tokens, but expect potential bugs.

# Tokens

## Creating a Dataverse API key
  - This must be for the dataverse installation you will work with.
  - Find or create this under https://data.qdr.syr.edu/dataverseuser.xhtml?selectTab=apiTokenTab (substitute the domain if not using QDR)

## Creating a Fine-Grained GitHub Personal Access Token

1. Go to your GitHub account settings
   - Click your profile photo in the top right
   - Select **Settings**

2. Navigate to Developer settings
   - Scroll to the bottom of the left sidebar
   - Click **Developer settings**
   - Select **Personal access tokens**
   - Click **Fine-grained tokens**
   - Click **Generate new token**

3. Configure token settings
   - Give your token a descriptive name (e.g., "DVCurator Access")
   - Choose "QualitativeDataRepository" as the resource owner
   - Select the repository "Project-Curation"
   - Under "Repository permissions", enable:
     - [x] **Actions** (Read and write)
       - Needed for triggering workflow dispatches
     - [x] **Issues** (Read)
       - Needed for checking existing tickets, to make sure we don't create duplicates

4. Generate and save the token
   - Click **Request** at the bottom and ask the admin to approve
   - **IMPORTANT**: Copy and save the token immediately

5. Using the token
   - In DVCurator, paste the token in the GitHub token field (under "DVCurator -> Configure Tokens")

# Other parameters
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

