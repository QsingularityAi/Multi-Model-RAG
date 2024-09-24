import os
import base64
from PIL import Image
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI
from IPython.display import display, HTML
from llms import get_multimodal_llm
import io
from base64 import b64decode
import matplotlib.pyplot as plt

current_working_directory = os.getcwd()
path = os.path.join(current_working_directory, 'Data')

def encode_image(image_path):
    ''' Getting the base64 string '''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



def image_summarize(img_base64, prompt):
    ''' Image summary '''
    chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=1024)  # Make sure llm2 is an instance of a class that can invoke a language model
    
    try:
        msg = chat.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            },
                        },
                    ]
                )
            ]
        )
        
        if isinstance(msg, str):
            return msg  # If the response is a string
        elif hasattr(msg, 'content'):
            return msg.content  # If the response is an object with a 'content' attribute
        else:
            return str(msg) 
    except Exception as e:
        # Catch any other exception that might occur
        print(f"An error occurred during image summarization: {e}")
        return str(e)  # Return the error as a string

def resize_image(image_path, base_width=300):
    img = Image.open(image_path)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    # Use Image.Resampling.LANCZOS or Image.LANCZOS for compatibility
    img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
    img.save(image_path)  # Save the resized image

# Prompt
prompt = """You are an assistant tasked with summarizing images for retrieval. \
These summaries will be embedded and used to retrieve the raw image. \
Give a concise summary of the image that is well optimized for retrieval. \
Describe the image in detail. Be specific about graphs, such as bar plots, curves."""

def process_images(path, prompt):
    img_base64_list = []
    image_summaries = []
    for img_file in sorted(os.listdir(path)):
        if img_file.endswith('.jpg'):
            img_path = os.path.join(path, img_file)
            resize_image(img_path)
            base64_image = encode_image(img_path)
            img_base64_list.append(base64_image)
            try:
                image_summary = image_summarize(base64_image, prompt)
                image_summaries.append(image_summary)
            except AttributeError as e:
                print(f"An error occurred: {e}")
    return img_base64_list, image_summaries

def plt_img_base64(img_base64):

    # Create an HTML img tag with the base64 string as the source
    image_html = f'<img src="data:image/jpeg;base64,{img_base64}" />'

    # Display the image by rendering the HTML
    display(HTML(image_html))
    
    
def split_image_text_types(docs):
    ''' Split base64-encoded images and texts '''
    b64 = []
    text = []
    for doc in docs:
        try:
            # This will decode the base64 string; if it fails, the string is likely not base64 encoded
            b64decode(doc, validate=True)
            b64.append(doc)
        except Exception as e:
            text.append(doc)
    return {
        "images": b64,
        "texts": text
    }

def plt_img_base64(base64_str):
    ''' Display a base64-encoded image using matplotlib '''
    image = Image.open(io.BytesIO(b64decode(base64_str)))
    plt.imshow(image)
    plt.axis('off')
    plt.show()
        
# def img_prompt_func(data_dict):
#     # Joining the context texts into a single string
#     formatted_texts = "\n".join(data_dict["context"]["texts"])
#     messages = []

#     # Adding image(s) to the messages if present
#     if data_dict["context"]["images"]:
        
#         image_data = base64.b64decode(data_dict["context"]["images"][0])
#         image = Image.open(io.BytesIO(image_data))
#         display(image)  # Display the image in the Jupyter notebook

#         image_message = {
#             "type": "image_url",
#             "image_url": {
#                 "url": f"data:image/jpeg;base64,{data_dict['context']['images'][0]}"
#             },
#         }
#         messages.append(image_message)

#     # Adding the text message for analysis
#     text_message = {
#         "type": "text",
#         "text": (
#             "Answer the question based only on the provided context, which can include text, tables, and image(s). "
#             "If an image is provided, analyze it carefully to help answer the question.\n"
#             f"User-provided question / keywords: {data_dict['question']}\n\n"
#             "Text and / or tables:\n"
#             f"{formatted_texts}"
#         ),
#     }
#     messages.append(text_message)
#     return [HumanMessage(content=messages)]