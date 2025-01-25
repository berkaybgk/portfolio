# Import packages
from .required_tools import GetAvailableDescriptions, MakeInternetSearch, GetPDFContent, GetResponse
from crewai import Agent, Crew, Process, Task, LLM
from pydantic import BaseModel

class Pdf_Name(BaseModel):
    pdf_name: str

class AgenticUtils:
    def __init__(self):
        print("Inside the AgenticUtils class")
        self.llm = LLM(model="llama-3.1-8b-instant")
        print("LLM model loaded")
        self.resource_agent = self.get_resource_extractor_agent()
        print("Resource agent loaded")
        self.response_agent = self.get_response_creator_agent()
        print("Response agent loaded")
        self.resource_task = self.get_resource_task()
        print("Resource task loaded")
        self.response_task = self.get_response_task()
        print("Response task loaded")

    def get_resource_task(self):
        return Task(
            description="""
            By checking out the available PDFs and their descriptions, you will decide if the available resources can help answer the user's question.
            If so, by extracting the content of the PDFs, you will be able to find the information that can answer the user's question.
            If not, you will use the internet to search for information that can help answer the user's question.
            """,
            expected_output="The resources that can help answer the user's question.",
            agent=self.resource_agent
        )

    def get_response_task(self):
        return Task(
            description="""
            By using the resources gathered by the Resource Extractor, you will create a response that answers the user's question.
            """,
            expected_output="A response that answers the user's question.",
            agent=self.response_agent
        )

    def get_resource_extractor_agent(self):
        agent = Agent(
            role="Resource Extractor",
            goal="Getting information from either the user's previously shared files or the internet which will help answer the user's question.",
            backstory="You will have access to the files of the user and their descriptions which will help you "
                      "determine if there are any PDFs that contain the information that can answer the user's question. After checking"
                      "the descriptions of the PDFs, you will be able to retrieve the content of the PDFs to find the resources related to the question. "
                      "If no pdf and descriptions are found relevant to the question, you can use the internet to search for information.",
            llm=self.llm,
            max_iter=3,
            tools=[GetAvailableDescriptions, GetPDFContent, MakeInternetSearch]
        )
        return agent

    def get_response_creator_agent(self):
        agent = Agent(
            role="Response Creator",
            goal="Creating a response based on the information extracted from the resources.",
            backstory="You will use the resources gathered by the Resource Extractor to create a response that answers the user's question.",
            llm=self.llm,
            max_iter=3,
            tools=[GetResponse]
        )
        return agent


class QuestionAnsweringCrew:
    def __init__(self):
        print("Inside tje question answering crew class")
        self.agentic_utils = AgenticUtils()

    def crew(self) -> Crew:
        return Crew(
            agents=[self.agentic_utils.resource_agent, self.agentic_utils.response_agent],
            tasks=[self.agentic_utils.resource_task, self.agentic_utils.response_task],
            process = Process.sequential,
            verbose=True
        )