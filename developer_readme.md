# Developers

## Running/compiling

dvcurator is written to be run either as a native python program or compiled with pyinstaller.

There are two spec files, `win.spec` and `mac.spec` to create native Windows or Mac applications. NOTE: you need to be on the platform in question to compile a native executable!

## Program organization

dvcurator is organized with `gui.py` as the top-level file, which calls on functions from the other `.py` files.

`gui.py` sets up the Tkinter GUI, collects input variables, and calls external functions. No actual processing should be done in this file, with the exception of minimal error handling. All practical processing is contained in the other `.py` files.

`hosts.py` sets a few key variables that end-users will probably not need to adjust themselves. This includes the hostname for the dataverse instance, and the Github repository to post to.

`fs.py` handles general client-side filesystem operations on the dropbox folder, such as creating a new folder for a processing step. 

`rename.py` generates names of files and folders from Dataverse metadata. This is for the "Basic rename" function in the edit menu

`pdf.py` contains all PDF related operations, namely generating and adding metadata. This is for the "PDF metadata" function in the edit menu

`readme.py` contains the functions that generate the README.txt file for a project from dataverse metadata.

`convert.py` is a wrapper the docx2pdf library.

`github.py` has functions to handle all github API calls.

`version.py` is set to git-development by default, which gets overwritten when one compiles a pyinstaller binary. This is used for checking whether or not dvcurator is up to date