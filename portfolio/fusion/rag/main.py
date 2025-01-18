from pprint import pprint
from dotenv import load_dotenv

# load the environment variables
load_dotenv()

# from .groq_client import GroqClient
from .vector_db_utils import VectorDbUtils
from .pdf_utils import PDFUtils

# gq = GroqClient()

pdf_utils = PDFUtils()

def handle_pdf_upload(username, pdf_name, pdf_description, pdf_file):
    vector_db = VectorDbUtils()

    pdf_name_valid = vector_db.check_pdf_name(pdf_name, username)

    if not pdf_name_valid:
        print("PDF already exists.")
        return False

    chunks = pdf_utils.get_chunks_from_pdf(1000, pdf_file, pdf_path=None)

    # Add the contents of the pdf to its own collection
    vector_db.create_collection(pdf_name, username)
    vector_db.upload_chunks(pdf_name, username, chunks)

    # Add the description of the pdf to the description collection
    vector_db.add_to_description_collection(username, pdf_name, pdf_description)

    return True


if __name__ == "__main__":
    # check the collection names
    # pprint(vector_db.client.list_collections())
    pass








