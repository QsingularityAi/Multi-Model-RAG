from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_community.embeddings import OpenAIEmbeddings
import uuid
from typing import List
from langchain.schema.document import Document
from process_pdfs import process_pdfs
from langchain_core.prompts import ChatPromptTemplate
from llms import get_multimodal_llm
from langchain.schema import StrOutputParser
from langchain import hub
from image_processing import encode_image, resize_image, plt_img_base64, process_images
from dotenv import load_dotenv
import os
load_dotenv()

def create_documents_and_vectorstore(texts, text_summaries, tables, table_summaries, img_base64_list, image_summaries):
    documents = []
    retrieve_contents = []

    for e, s in zip(texts, text_summaries):
        i = str(uuid.uuid4())
        doc = Document(
            page_content=s,
            metadata={
                'id': i,
                'type': 'text',
                'original_content': e
            }
        )
        retrieve_contents.append((i, e))
        documents.append(doc)
    
    for e, s in zip(tables, table_summaries):
        i = str(uuid.uuid4())
        doc = Document(
            page_content=s,
            metadata={
                'id': i,
                'type': 'table',
                'original_content': e
            }
        )
        retrieve_contents.append((i, e))
        documents.append(doc)
    
    for e, s in zip(img_base64_list, image_summaries):
        i = str(uuid.uuid4())
        doc = Document(
            page_content=s,
            metadata={
                'id': i,
                'type': 'image',
                'original_content': e
            }
        )
        retrieve_contents.append((i, s))
        documents.append(doc)

    if documents:
        vectorstore = Chroma.from_documents(documents=documents, embedding=OpenAIEmbeddings(), persist_directory="./chroma_db")
    else:
        vectorstore = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="./chroma_db")
    
    return vectorstore

# Call the function:
# populate_retriever(retriever2, texts, text_summaries, tables, table_summaries, img_base64_list, image_summaries)

rag_prompt_mistral = hub.pull("rlm/rag-prompt-mistral")
# Specify the directory containing the PDFs
current_working_directory = os.getcwd()
path = os.path.join(current_working_directory, 'Data')
# Separate tables and text elements
raw_pdf_elements = process_pdfs(path)

def tex_tab_elements():
    tables = []
    texts = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            tables.append(str(element))
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            texts.append(str(element))
    return tables, texts
# Function to create summarization chain
def create_summarization_chain(prompt_text, llm):
    prompt = ChatPromptTemplate.from_template(prompt_text)
    model = llm
    return {"element": lambda x: x} | prompt | model | StrOutputParser()

# Function to summarize text data
def text_summaries(texts, prompt_text, llm):
    summarization_chain = create_summarization_chain(prompt_text, llm)
    return summarization_chain.batch(texts, {"max_concurrency": 5})

# Function to summarize table data
def table_summaries(tables, prompt_text, llm):
    summarization_chain = create_summarization_chain(prompt_text, llm)
    return summarization_chain.batch(tables, {"max_concurrency": 5})

# Initialize path, prompt, and LLM
prompt_text = """You are an assistant tasked with summarizing tables and text. \
Give a concise summary of the table or text. Table or text chunk: {element} """
#llm = getLLM_SauerkrautLM()
llm = get_multimodal_llm()

# Load table and text data
tables, texts = tex_tab_elements()

# Summarize the text and table data
text_summaries = text_summaries(texts, prompt_text, llm)
table_summaries = table_summaries(tables, prompt_text, llm)

# Prompt
prompt = """You are an assistant tasked with summarizing images for retrieval. \
These summaries will be embedded and used to retrieve the raw image. \
Give a concise summary of the image that is well optimized for retrieval. \
Describe the image in detail. Be specific about graphs, such as bar plots, curves."""

img_base64_list, image_summaries = process_images(path, prompt)



def load_retriever_instance():
    retriever_instance = create_documents_and_vectorstore( 
                                        texts, text_summaries, 
                                        tables, table_summaries, 
                                        img_base64_list, image_summaries)
    return retriever_instance 
