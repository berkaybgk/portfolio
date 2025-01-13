def parse_ds_project_info(readme_file_path):
    with open(readme_file_path, 'r') as file:
        project_description = file.read()

    # Split the readme file into sections
    sections = project_description.split('\n\n\n')

    # Get the project title
    title = sections[0].strip().strip("***").strip()

    # Get the project description
    description = sections[1].strip().strip("**").strip()

    # Get the url of the project
    url = sections[2].strip().strip("**").strip()

    return title, description, url