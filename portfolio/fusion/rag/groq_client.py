import groq
import os
from dotenv import load_dotenv
from crewai import Agent

load_dotenv()

class GroqClient:
    def __init__(self):
        self.client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"

    def get_response(self, user_message):
        return self.client.chat.completions.create(
            messages=[
            {
                "role": "system",
                "content": "You are an expert in teaching and assisting with classes. "
                           "The user will ask you questions about classes and you will answer them. "
                           "Be very concise and clear in your answers. Provide short and concise answers but convince "
                           "the user that you actually know about the things he asks. If the question is not related to classes, "
                           "say that you don't know the answer. Don't introduce yourself and don't ask questions. "
            },
            {
                "role": "user",
                "content": f"{user_message}",
            }
        ],
            model=self.model
        ).choices[0].message.content


