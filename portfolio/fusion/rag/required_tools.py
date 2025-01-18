from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from typing import Any

class DeterminePDFInput(BaseModel):
    question: str = Field(..., description="The question of the user")
    available_pdfs: dict = Field(..., description="The available PDFs that contain the information related to the user's question")

class DeterminePDF(BaseTool):
    name: str = "determine_pdf"
    description: str = "Determine the PDF that contains the information related to the user's question"
    args_schema: Type[BaseModel] = DeterminePDFInput

    def _run(self, argument: DeterminePDFInput) -> Any:
        pdfs = argument.available_pdfs
        question = argument.question

        for pdf, content in pdfs.items():
            for word in question.split():
                if word.lower() in content.split("about")[1].lower():
                    return pdf, content

        return "No PDF found"