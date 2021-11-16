# dvcurator -- A set of common Dataverse Curation tasks

The tool is based on QDR's curation practices and will likely require modifications for other repositories.

# Functionality

1. Creating github issues for standard curation tasks and associating them with a github Project for the curation of the data project.
2.  Creating a local curation folder with subfolders for Original Deposit and QDR Prepared (this should typically be in Dropbox)
3. Downloading the .zip file for the full data project to the Original Deposit folder and an unzipped version to QDR Prepared for further Curation

# Requirements

The tool requires the following options to be set:
* A **github token** using the -g <token> or --ghtoken <token> command line option
  * To create a github token, go to your github developer settings/personal access tokens at https://github.com/settings/tokens
  * Click on "Generate New Token"
  * Give the token a recognizable name such as "QDR Curation" and check the following boxes:
    * repo
    * admin:org 
    * notifications
    * write:discussion
  * Click "Generate Token" at the bottom of the screen. Make sure to note down your token and keep it safe (you won't be able to access this later)
* A **dataverse API key** using the -v <token> or --dvtoken <token> command line option - this must be for the dataverse installation you will work with.
  * Find or create this under https://data.qdr.syr.edu/dataverseuser.xhtml?selectTab=dataRelatedToMe (substitute the domain if not using QDR) --> API Token
