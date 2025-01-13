import os
import json

def parse_analysis_content(ds_project_folder_path):
    """
    This function parses the content of the analysis folder of a data science project.
    The folder contains three files:
    - eda.ipynb
    - main.py
    - model_eval.ipynb

    :param ds_project_folder_path: The path to the data science project folder.
    :return: A tuple (eda_content, main_content, eval_content), where each element is the
             content of the respective file as a string or None if the file is not found.
    """
    eda_content = None
    main_content = None
    eval_content = None

    def extract_notebook_content(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Extract code cell content, handling cases where "source" is a list
                content = "\n".join(
                    "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
                    for cell in data.get("cells", [])
                    if cell["cell_type"] == "code"
                )
                return content
        except Exception as e:
            print(f"Error parsing notebook content at {file_path}: {e}")
            return None

    try:
        # Paths to the files
        eda_path = os.path.join(ds_project_folder_path, "eda.ipynb")
        main_path = os.path.join(ds_project_folder_path, "main.py")
        eval_path = os.path.join(ds_project_folder_path, "model_eval.ipynb")

        # Read and parse eda.ipynb
        if os.path.exists(eda_path):
            eda_content = extract_notebook_content(eda_path)

        # Read and parse main.py
        if os.path.exists(main_path):
            with open(main_path, "r", encoding="utf-8") as main_file:
                main_content = main_file.read()

        # Read and parse model_eval.ipynb
        if os.path.exists(eval_path):
            eval_content = extract_notebook_content(eval_path)

    except Exception as e:
        print(f"Error parsing analysis content: {e}")

    return eda_content, main_content, eval_content



if __name__ == '__main__':
    # Test the function
    eda, main, eval = parse_analysis_content('/Users/berkaybgk/Desktop/cs related/python_files/datamata/mushroom/')

    print("EDA Content:")
    print(eda)

    print("\nMain Content:")
    print(main)

    print("\nEvaluation Content:")
    print(eval)

