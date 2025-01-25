from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
from typing import Type
from typing import Any
from .vector_db_utils import VectorDbUtils
from .groq_client import GroqClient

class GetPDFDescriptionsInput(BaseModel):
    username: str = Field(..., description="The username of the user, must be exact character by character")
    question: str = Field(..., description="The question of the user")

class GetAvailableDescriptions(BaseTool):
    name: str = "get_pdfs_descriptions"
    description: str = "Get the available PDF names and their descriptions about their content"
    args_schema: Type[BaseModel] = GetPDFDescriptionsInput

    def _run(self, argument: GetPDFDescriptionsInput) -> Any:
        vdb = VectorDbUtils()

        description_collection = vdb.get_description_collection(argument.username)

        related_pdfs = description_collection.query(
            query_texts=argument.question,
            n_results=3
        )

        pdf_names = related_pdfs.get("ids", [])
        pdf_descriptions = related_pdfs.get("documents", [])

        return zip(pdf_names, pdf_descriptions)


class InternetSearchInput(BaseModel):
    question: str = Field(..., description="The key question to search the internet for, which will then help answer the user's question")

class MakeInternetSearch(BaseTool):
    name: str = "make_internet_search"
    description: str = "Search the internet for the key question to help answer the user's question"
    args_schema: Type[BaseModel] = InternetSearchInput

    def _run(self, argument: InternetSearchInput) -> Any:
        tc = TavilyClient()
        response = tc.search(argument.question)

        response = response.get("results", [])

        if not response:
            response = "No results found on the internet"
            return response

        else:
            return (response[0].get("title") + "\n" + response[0].get("content") + "\n\n"
                    + response[1].get("title") + "\n" + response[1].get("content"))


class GetPDFContentInput(BaseModel):
    pdf_name: str = Field(..., description="The name of the PDF to get the content from")
    username: str = Field(..., description="The username of the user")

class GetPDFContent(BaseTool):
    name: str = "get_pdf_content"
    description: str = "Get the content of the PDF previously uploaded by the user"
    args_schema: Type[BaseModel] = GetPDFContentInput

    def _run(self, argument: GetPDFContentInput) -> Any:
        vdb = VectorDbUtils()
        collection = vdb.get_collection_by_collection_name(argument.pdf_name)

        chunks = collection.query(
            query_texts="",
            n_results=3
        )

        return "\n".join(chunks.get("documents", []))

class GetResponseInput(BaseModel):
    user_message: str = Field(..., description="The message sent by the user")
    all_related_info: str = Field(..., description="All the related information to help answer the user's question")

class GetResponse(BaseTool):
    name: str = "get_response"
    description: str = "Get the response to the user's question"
    args_schema: Type[BaseModel] = GetResponseInput

    def _run(self, argument: GetResponseInput) -> Any:
        user_messages = argument.user_message
        all_related_info = argument.all_related_info

        gq = GroqClient()

        return gq.get_answering_results(user_messages, all_related_info)

