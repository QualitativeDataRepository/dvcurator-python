# dvcurator -- A set of common Dataverse Curation tasks

The tool is based on QDR's curation practices and will likely require modifications for other repositories.

# Functionality

1. Creating github issues for standard curation tasks and associating them with a github Project for the curation of the data project.
2. Creating a local curation folder with subfolders for Original Deposit and QDR Prepared (this should typically be in Dropbox)
3. Downloading the .zip file for the full data project to the Original Deposit folder and an unzipped version to QDR Prepared for further Curation
4. Automatically setting metadata for PDF files

# Installing

This package can be installed with pip. 

If you have both pip and git installed, this package can be downloaded and installed directly with:

`pip install git+https://github.com/QualitativeDataRepository/dvcurator-python`

Otherwise, this package can be installed from a zip file:

`pip install dvcurator-python-master.zip`

# Executing

Three run-time parameters must be specified: a config file, and a dataverse persistent ID for the project to curate.

`dvcurator -c <config.ini> -d <doi:xxxxxx/xxxxxx> issues/`

# Requirements

Two packages are required: `requests` and `pdfrw`.

An .ini file is used to configure program parameters. This config file must be specificed on the command line with the `-c` or `--config` options. The included file `config.ini.default` can be used as a template.

To be fully functional, the following parameters must be set in the config file:
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
  * Find or create this under https://data.qdr.syr.edu/dataverseuser.xhtml?selectTab=dataRelatedToMe (substitute the domain if not using QDR) --> API Token

Other parameters are:
- Dropbox folder: Where the archive will be downloaded and extracted to. Usually points to a folder that syncs with Dropbox.
- Repo: Which github repository to post the issues
- Host: Where the dataverse instance is hosted.
