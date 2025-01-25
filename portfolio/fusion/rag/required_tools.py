from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from typing import Any
from .vector_db_utils import VectorDbUtils

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
    description: str = "Searches the internet to find an answer for a given key question"
    args_schema: Type[BaseModel] = InternetSearchInput

    def _run(self, argument: GetPDFDescriptionsInput) -> Any:
        return f"Searching the internet for the question: {argument.question}"