# Import packages
from required_tools import GetAvailableDescriptions, GetPDFDescriptionsInput
from crewai import Agent, Crew, Process, Task, LLM
from pydantic import BaseModel

class Pdf_Name(BaseModel):
    pdf_name: str

class AgenticUtils:
    def __init__(self):
        self.llm = LLM(model="llama-3.1-8b-instant")

    def get_pdf_determining_agent(self):
        agent = Agent(
            role="PDF Determining Agent",
            goal="Determine the file name that contains the information related to the user's question",
            backstory="You will have access to the files of the user and their descriptions, which will help you "
                      "determine the PDF that contains the information related to the user's question.",
            llm=self.llm,
            max_iter=3,
            tools=[GetAvailableDescriptions]
        )
        return agent



"""
from typing import Optional, Tuple, Union

def validate_json_output(result: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
    ""Validate and parse JSON output.""
    try:
        # Try to parse as JSON
        data = json.loads(result)
        return (True, data)
    except json.JSONDecodeError as e:
        return (False, {
            "error": "Invalid JSON format",
            "code": "JSON_ERROR",
            "context": {"line": e.lineno, "column": e.colno}
        })

task = Task(
    description="Generate a JSON report",
    expected_output="A valid JSON object",
    agent=analyst,
    guardrail=validate_json_output,
    max_retries=3  # Limit retry attempts
)
"""






