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

*NOTE:* Syracuse University office computers cannot run this program directly because of security policies. You should download the [SU Lab Install.ps1](https://github.com/QualitativeDataRepository/dvcurator-python/blob/master/SU%20Lab%20Install.ps1) file (right click "Raw" and the top and Save Link As), and run that instead by right-clicking and selecting "Run with PowerShell". This will install the program properly and create a shortcut on your desktop.

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
     - [x] **Contents** (Read)
       - Needed to download the README template  
     - [x] **Issues** (Read)
       - Needed for checking existing tickets, to make sure we don't create duplicates

4. Generate and save the token
   - Click **Request** at the bottom and ask the admin to approve
       - Admins: [Approve the token here](https://github.com/organizations/QualitativeDataRepository/settings/personal-access-token-requests)   
   - **IMPORTANT**: Copy and save the token immediately

5. Using the token
   - In DVCurator, paste the token in the GitHub token field (under "DVCurator -> Configure Tokens")

# How project creation works

"Make github project" does not create the project directly. It triggers a workflow in the
curation repository, which creates the GitHub Project and its issues on your behalf.

This is why your own token only needs Actions read/write: creating an organization-level
Project needs broader permissions than we hand out to curators, so that credential stays
in the curation repository and is never distributed with dvcurator.

One consequence worth knowing: **"Project creation request sent successfully" only means
the request was accepted**, not that the project was created. If no project appears
afterwards, the workflow failed on the server side. That is not a problem with your token
and regenerating it will not help -- contact a repository admin, who can check the
workflow run and its logs.

# Naming

Projects and Dropbox folders are named `YYYYMMDD - Lastname`, using the **Deposit Date**
from Dataverse and the first author's last name. Leading with the date means folders sort
chronologically. The folder is named exactly that, e.g. `20220608 - Haney`. The old
`QDR Project - ` prefix is gone, which gives back 14 characters of headroom on every path
inside a project against Windows' 260 character path limit.

A few deposits, mostly older migrated ones, record only a year as their deposit date. In
those cases dvcurator falls back to the date the version was created and prints a warning
saying so.

If you have folders from before this convention, which were named after the deposit title,
dvcurator will still find them: when it can't locate a folder with the current name it
looks for any folder matching the author. It only does this when exactly one folder
matches -- if there are several it lists them and asks you to pick one from
"File processing -> Select project subfolder manually".

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

To run from a checkout without installing, install the requirements and run the module
from the repository root:

```
python -m pip install -r requirements.txt
python -m dvcurator
```

Run it from the repository root specifically: settings are read from and written to
`dvcurator.ini` in the *current working directory*, so launching from elsewhere gives you
a different config. If you already use the packaged .exe, copying its `dvcurator.ini`
into the repository root brings your tokens and folder across.

`config.ini.default` is a template you can copy to `dvcurator.ini` and fill in by hand.

### Making a release

Releases are driven by tags. Pushing a tag starting with `v` triggers
`.github/workflows/build.yml`, which rewrites `dvcurator/version.py` from the tag, builds
the Windows executable with pyinstaller, and opens a **draft** release with the .exe
attached. Only Windows is built -- `mac.spec` exists but no workflow uses it.

Use `release.py`, which checks the repository over and creates the tag:

```
python release.py v1.1.3
```

It refuses to tag unless tracked files are all committed, you are on `master`, the version
isn't already tagged locally or on origin, master isn't behind origin, and the test suite
passes. Pass `--skip-tests` to skip the last of those.

Tests run with the same interpreter you invoke the script with, so run it with the Python
that has the requirements installed -- e.g. `.venv\Scripts\python release.py v1.1.3`. It
checks the dependencies are importable before running anything and tells you what to
install if they aren't.

It then shows you what it's about to push and asks before doing it. `--yes` skips the
question; `--no-push` creates the tag and stops, printing the commands so you can push by
hand. Answering no leaves the tag in place, which you can drop again with
`git tag -d v1.1.3`.

If master has commits that aren't on origin yet, it pushes the branch before the tag --
otherwise the release gets built from commits that aren't on the branch.

**Then publish the draft release.** This is easy to forget and fails quietly:
`SU Lab Install.ps1` resolves `/releases/latest`, which ignores drafts, so until you
publish, the lab installer keeps handing out the previous version without any error.

