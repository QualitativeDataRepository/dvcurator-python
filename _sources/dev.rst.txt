Developers overview
*******************

Running/compiling
=================

dvcurator is written to be run either as a native python program or compiled with pyinstaller.

To run as an interpreted program, dvcurator is a python package. From within a freshly cloned repo, you can run the program with `python -m dvcurator` or install with `python -m pip install dvcurator`

There are two spec files, `win.spec` and `mac.spec` to create native Windows or Mac applications with pyinstaller, e.g. `pyinstaller mac.spec`. NOTE: you need to be on the platform in question to compile a native executable!

Program organization
====================

dvcurator is organized with `gui.py` as the top-level file, which calls on functions from the other `.py` files.

`gui.py` sets up the Tkinter GUI, collects input variables, and calls external functions. No actual processing should be done in this file, with the exception of minimal error handling. All practical processing is contained in the other `.py` files.

`hosts.py` sets a few key variables that end-users will probably not need to adjust themselves. This includes the hostname for the dataverse instance, and the Github repository to post to. These variables only really need to be adjusted for debugging, and so are essentially hard-coded into the compiled .exe/.app files.

`fs.py` handles general client-side filesystem operations on the dropbox folder, such as creating a new folder for a processing step. 

`rename.py` generates names of files and folders from Dataverse metadata. This is for the "Basic rename" function in the edit menu

`pdf.py` contains all PDF related operations, namely generating and adding metadata. This is for the "PDF metadata" function in the edit menu

`readme.py` contains the functions that generate the README.txt file for a project from dataverse metadata.

`convert.py` is a wrapper the docx2pdf library.

`github.py` has functions to handle all github API calls. `github_projectsv2.py` replicates these calls for the new ProjectsV2 api.

`version.py` is set to git-development by default, which gets overwritten when one compiles a pyinstaller binary. This is used for checking whether or not dvcurator is up to date

Compilation process
===================

This program is meant to be run as a compiled .exe or .app file, and run natively. These binaries are created with github actions. 

The compilation process is not triggered by regular pushes. Any time a new **tag** is pushed, Github will compile a new executable. These executables are uploaded as draft **releases**, not immediately available. To make a new release publicly available, publish the draft release.

To summarize, the following steps compile a new native executable and make it available:

* Push a new tag
* Wait for the compilation process to finish (check github actions)
* Test the new draft executable (if you want) under releases
* Publish the draft release

dvcurator checks for new *tags* (because of API limitations) every time it is launched to alert users when there is a new version available.
