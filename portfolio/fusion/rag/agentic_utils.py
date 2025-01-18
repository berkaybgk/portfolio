# Import packages
from required_tools import DeterminePDFInput, DeterminePDF

class AgenticUtils:
    def __init__(self, model_name):
        self.model_name = model_name

        self.available_pdfs = {
            "pdf1": "This pdf contains information about operating systems",
            "pdf2": "This pdf contains information about databases",
            "pdf3": "This pdf contains information about programming languages",
        }

        self.determine_pdf_tool = DeterminePDF()

    def get_answering_pdf(self, question):
        return self.determine_pdf_tool.run(DeterminePDFInput(question=question, available_pdfs=self.available_pdfs))



if __name__ == "__main__":

    agentic_utils = AgenticUtils("llama3-8b-8192")

    question = "What is the best programming language to learn?"

    pdf, content = agentic_utils.get_answering_pdf(question)

    print(f"The PDF that contains the information related to the question '{question}' is: {pdf, content}")









