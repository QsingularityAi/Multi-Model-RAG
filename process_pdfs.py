import os
import uuid
from langchain_community.document_loaders import PyPDFLoader
from unstructured.partition.pdf import partition_pdf

def process_pdfs(pdf_directory):
    """
    Processes all PDFs in a directory, extracting elements and saving summaries.

    Args:
        pdf_directory (str): Path to the directory containing PDFs.

    Returns:
        list: A list of dictionaries containing extracted elements and summaries.
    """

    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    all_elements = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        extracted_elements = partition_pdf(
            filename=pdf_path,
            extract_images_in_pdf=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
            image_output_dir_path= os.path.join(os.getcwd(), "Data")  # Assuming images are saved in the same directory
        )
        if extracted_elements:
            all_elements.extend(extracted_elements)

    return all_elements

# # Example usage (replace with your actual directory path)
# path= "/home/anurag/chatbot-intranet/Simson_chatbot/Data"
# raw_pdf_elements = process_pdfs(path)


# def tex_tab_elements():
#     tables = []
#     texts = []
#     for element in raw_pdf_elements:
#         if "unstructured.documents.elements.Table" in str(type(element)):
#             tables.append(str(element))
#         elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
#             texts.append(str(element))
#     return tables, texts


