# check whether dropbox folder is set correctly
def check_dropbox(dropbox, project_name=None):
    """
    Check whether the specified dropbox folder is accessible

    :param dropbox: Path to dropbox folder
    :type dropbox: path as a string
    :param project_name: Project name to check if there is an existing folder in dropbox
    :type project_name: String

    """
    import os.path
    from glob import glob
    if not os.path.exists(dropbox):
        print("Dropbox folder not found: " + dropbox) 
        return None
    if not project_name:
        # check if there's any existing "QDR Project - " folders
        test_folders = glob(os.path.join(dropbox, "QDR Project - *"))
        if (len(test_folders) < 1):
            print("ALERT: No existing QDR project folders found in: " + dropbox)
            print("Continuing anyway...")
    else:
        folder_name = 'QDR Project - ' + project_name
        path = os.path.normpath(os.path.join(dropbox, folder_name))
        if os.path.exists(path):
            return path
        else:
            print("Project folder does not exist: " + path)
            return None

    # return true as long as the dropbox path exists if we're not checking for the subfolder
    return True

def recursive_scan(path):
    """
    List all files in folder, recursively. Used to generate file list in README

    :param path: Path to folder
    :type path: Path as string
    :return: Pretty-printed recursive file list
    :rtype: String

    """
    import os
    output = []
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level-1)
        output.append('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level)
        for f in files:
            output.append('{}{}'.format(subindent, f))

    output = output[1:] # remove first item (like "./")
    output = '\n'.join(output)
    return output

# What is the latest folder under QDR Prepared?
def current_step(folder):
    """
    Find latest (highest numbered) step in the "QDR Prepared" subfolder, i.e. "4_metadata"

    :param folder: Folder to check, should be path to "QDR Prepared" folder
    :type folder: Path, as string
    :return: Path to subfolder with highest number, or None in case of error
    :rtype: Path as a string, or None

    """
    from glob import glob
    import os.path
    if not os.path.isdir(folder):
        print("Error: not a folder " + folder)
        return None
    candidates = sorted(glob(os.path.join(folder, "[0-9]_*")))
    if (len(candidates) < 1):
        print("Error: no folders found under " + folder)
        return None
    current = candidates[len(candidates)-1]
    return current

# Copy QDR prepared latest step to a new step, incrementing step number
def copy_new_step(folder, step):
    """
    Copy QDR Prepared latest step (i.e. 3_rename) to a new step (i.e. 4_metadata), incrementing step number

    :param folder: "QDR Prepared" folder
    :type folder: Path, as string
    :param step: Short description of next step, e.g. "metadata" or "rename"
    :type step: String
    :return: Path to newly created folder
    :rtype: String

    """
    #exists = check_dropbox(dropbox, project_name)
    #if not exists:
    #    return None
    import os.path
    if not os.path.exists(folder):
        print("Subfolder not detected: " + folder)
        return None

    import os.path
    from shutil import copytree
    edit_path = os.path.normpath(os.path.join(folder, "QDR Prepared"))
    current = current_step(edit_path)
    if not current:
        return None
    number = int(os.path.split(current)[1].split("_")[0]) + 1
    new_step = str(number) + "_" + step
    copytree(os.path.join(edit_path, current), os.path.join(edit_path, new_step))
    return os.path.join(edit_path, new_step)

def anonymize_project(folder, citation):
    """
    Run full anonymization routine. Calls anon routine for filenames and PDF metadata

    :param folder: Project folder
    :type folder: path, as string
    :param citation Dataverse citation
    :return: Path to new folder
    :rtype: string
    """
    import dvcurator.pdf, dvcurator.rename
    edit_path = copy_new_step(folder, "anonymized")
    if not edit_path:
        return None

    dvcurator.rename.anonymize(edit_path, citation)
    print("\n")
    dvcurator.pdf.write_metadata(edit_path, "ANONYMIZED")

    return edit_path
