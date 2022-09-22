def clean_html_tags(text):
    import re
    tags = re.compile('<.*?>')
    clean_text = re.sub(tags, '', text)
    return clean_text

def generate_readme(metadata, folder, token=None):
    from string import Template
    from pkg_resources import resource_filename
    import os, dvcurator.dataverse, dvcurator.fs, dvcurator.rename, sys
    citation = dvcurator.dataverse.get_citation(metadata)
    folder = dvcurator.fs.current_step(folder)

    biblio_citation = dvcurator.dataverse.get_biblio_citation(
        metadata['data']['latestVersion']['datasetPersistentId'], 
        token)
    if not biblio_citation:
        print("Warning: dataverse token not authorized for this project, citation missing")
        # What string will go in the actual readme
        biblio_citation = "NOTICE: Citation unable to be automatically scraped from dataverse"
    
    # Some projects don't have defined access terms.
    # Handle these errors gracefully
    try:
        access = clean_html_tags(metadata['data']['latestVersion']['termsOfAccess'])
    except KeyError:
        access = "NOTICE: No access terms defined."
        print("Warning: No Terms of Access defined on Dataverse")

    d = {'title': citation['title'], 
        'citation': biblio_citation,
        'description': clean_html_tags(citation['dsDescription'][0]['dsDescriptionValue']['value']),
        'access': access,
        'files': "\n".join(os.listdir(folder))
    }

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        path = os.path.join(sys._MEIPASS, "templates", "README.txt")
    else:
        path = resource_filename("dvcurator", "templates/README.txt")

    readme_name = "README_" + dvcurator.rename.last_name_prefix(citation) + ".txt"
    new_path = os.path.join(folder, "..", readme_name)
    if os.path.exists(new_path):
        print("Error: README exists at " + new_path)
        return None

    with open(path, 'r') as f:
        src = Template(f.read())
        text = src.safe_substitute(d)
        with open(new_path, 'w') as n:
            n.write(text)
            print("Written: " + new_path)