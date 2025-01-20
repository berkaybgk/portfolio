"""
This module contains utility functions for PDF files.
We will use it to parse and chunk PDF files.
"""
from PyPDF2 import PdfReader


class PDFUtils:
    def __init__(self):
        pass

    def read_pdf(self, pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            pdf_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_text += page.extract_text()
        return pdf_text

    def get_chunks_from_pdf(self, chunk_size, pdf_file, pdf_path=None):
        if pdf_path is not None:
            pdf_text = self.read_pdf(pdf_path)
        else:
            pdf_reader = PdfReader(pdf_file)
            pdf_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_text += page.extract_text()
        chunks = [pdf_text[i:i+chunk_size] for i in range(0, len(pdf_text), chunk_size)]
        return chunks

    @staticmethod
    def get_chunks_from_text(chunk_size, text):
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        return chunks


