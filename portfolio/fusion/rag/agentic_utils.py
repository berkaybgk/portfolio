# Import packages
from required_tools import GetAvailableDescriptions, MakeInternetSearch
from crewai import Agent, Crew, Process, Task, LLM
from pydantic import BaseModel

class Pdf_Name(BaseModel):
    pdf_name: str

class AgenticUtils:
    def __init__(self):
        self.llm = LLM(model="llama-3.1-8b-instant")

    def get_resource_extractor_agent(self):
        agent = Agent(
            role="Resource Extractor",
            goal="Getting information from either the user's previously shared files or the internet which will help answer the user's question.",
            backstory="You will have access to the files of the user and their descriptions which will help you "
                      "determine if there are any PDFs that contain the information that can answer the user's question."
                      "You can also use the internet to search for information if no PDFs are found to answer the question.",
            llm=self.llm,
            max_iter=3,
            tools=[GetAvailableDescriptions, MakeInternetSearch]
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






