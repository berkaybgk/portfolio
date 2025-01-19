from pprint import pprint
from dotenv import load_dotenv
from ..models import Chat

# load the environment variables
load_dotenv()

from .groq_client import GroqClient
from .vector_db_utils import VectorDbUtils
from .pdf_utils import PDFUtils

pdf_utils = PDFUtils()
gq = GroqClient()

def handle_pdf_upload(username, pdf_name, pdf_description, pdf_file):
    vector_db = VectorDbUtils()

    pdf_name_valid = vector_db.check_pdf_name(pdf_name, username)

    if not pdf_name_valid: # Pdf name already exists
        return False

    chunks = pdf_utils.get_chunks_from_pdf(1000, pdf_file, pdf_path=None)

    # Add the contents of the pdf to its own collection
    vector_db.create_collection(pdf_name, username)
    vector_db.upload_chunks(pdf_name, username, chunks)

    # Add the description of the pdf to the description collection
    vector_db.add_to_description_collection(username, pdf_name, pdf_description)

    return True


def handle_message(user, current_message):

    try:
        # Get the last 5 messages
        chat_messages = Chat.objects.filter(user=user).order_by('-timestamp')[:5]

        user_messages = list(chat_messages.values_list('message', flat=True))
        ai_responses = list(chat_messages.values_list('response', flat=True))

        last_messages = list(zip(user_messages, ai_responses))
    except Exception as e:
        return "Sorry, I am having trouble since I am unable to retrieve the last messages. This is a temporary issue."

    gq_response = gq.get_response(current_message)

    return gq_response






