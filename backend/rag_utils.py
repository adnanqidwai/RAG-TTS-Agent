from PyPDF2 import PdfReader
import os
import chromadb 
from langchain.text_splitter import CharacterTextSplitter

PROMPT = """You are a helpful assistant who answers questions strictly based on the context you recieve.
If the query is not related to the context provided, output "I am sorry, I can't answer this question based on the provided context".
If it is answerable, provide the answer in a clear and concise technique.

Context: {context}
Question: {question}
"""

rag_generation_config = {
  "temperature": 0.5,
  "top_p": 0.95,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  }
]
# or any model

def generate_model_response(model, query: str, context: str) -> str:
    try:
        response = model.generate_content(PROMPT.format(context=context, question=query)).text
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}. The request ({query}) could not be processed."

def get_pdf_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text()
    return text

def clean_text(text):
    return text.replace('\n', ' ').replace('\x0c', ' ').replace('  ', ' ')


def chunk_by_tokens(text, chunk_size=300, chunk_overlap=50):
    splitter = CharacterTextSplitter(
        separator=" ",  # Split by spaces
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    
    return splitter.split_text(text)

def create_database(collection_name: str, path: str, pdf_directory: str) :
    print("Creating database")
    pdfs = os.listdir(pdf_directory)
    gathered_pdfs = [pdf for pdf in pdfs if pdf.endswith('.pdf')]
    text = ""
    for pdf in gathered_pdfs:
        text += get_pdf_text(f'{pdf_directory}/{pdf}')
    text = clean_text(text)
    chunks = chunk_by_tokens(text)
    client = chromadb.PersistentClient(path=path)
    collection = client.create_collection(collection_name)

    collection.add(
        ids = [f"{i}" for i in range(len(chunks))],
        documents= chunks
    )
    return