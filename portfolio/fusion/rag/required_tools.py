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
    description: str = "Get the available PDFs and their descriptions"
    args_schema: Type[BaseModel] = GetPDFDescriptionsInput

    def _run(self, argument: GetPDFDescriptionsInput) -> Any:
        vdb = VectorDbUtils()

        description_collection = vdb.get_description_collection(argument.username)

        related_pdfs = description_collection.query(
            query_texts=argument.question,
            n_results=8
        )

        pdf_names = related_pdfs.get("ids", [])
        pdf_descriptions = related_pdfs.get("documents", [])

        return zip(pdf_names, pdf_descriptions)
