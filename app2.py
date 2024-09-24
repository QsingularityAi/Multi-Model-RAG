import chainlit as cl
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from retriver import load_retriever_instance
from dotenv import load_dotenv
from PIL import Image
import io
import base64

# Load environment variables
load_dotenv()

# Pull the prompt template from the hub
rag_prompt_mistral = hub.pull("rlm/rag-prompt-mistral")

# Load the retriever instance
retriever_instance = load_retriever_instance()

# Function to load the model
def load_model():
    return ChatOpenAI(temperature=0, model="gpt-4-vision-preview", max_tokens=1024)

# Prompt template for the answer chain
answer_template = """
Answer the question based only on the following context, which can include text, images, and tables:
{context}
Question: {question} 
"""
answer_prompt = PromptTemplate.from_template(answer_template)

# Predefined questions
predefined_questions = [
    "Visualize an industrial setting where an orange-colored rugged tablet sits on a grey workbench. Include a display screen, a small metallic object beside the tablet, and a sticker with a blue circular symbol. The environment should reflect a technical or workshop space with the focus on the tablet as a tool for industrial operations.",
    "Describe the setup of a black automotive battery with yellow terminal caps, focusing on the attached red cable with a heavy-duty clamp and the shiny metal nuts and bolts lying on the battery. Emphasize the battery's protective features and its role in an automotive electrical system.",
    "Why are the yellow caps used on the positive and negative terminals of the battery?",
    "What are the key features visible in the top right corner of the automotive battery?",
    "What is the purpose of the rugged orange-colored electronic device shown in the image?",
    "What kind of electronic device is housed inside the rugged carrying case, and what are its functions?",
    "Can the MIRROR-ANALYSER SF6 be used with gas collecting bags? If so, how?",
    "What is the maximum number of measurements that can be stored on the MIRROR-ANALYSER SF6 device?",
    "What is the maximum inlet pressure that the MIRROR-ANALYSER SF6 can handle?",
    "How does the external compressor accessory enhance the function of the MIRROR-ANALYSER SF6?",
    "How does the MIRROR-ANALYSER SF6 determine the moisture concentration?",
    "What measurement principles are used for determining the SF6 volume percentage and SO2 concentration?",
    "What are the three quality parameters that the MIRROR-ANALYSER SF6 can measure in a single test?",
    "Which sensors are interchangeable in the MIRROR-ANALYSER SF6, and why is this feature important?",
    "Describe the role of the integrated gas return system in the MIRROR-ANALYSER SF6.",
    "What are the physical dimensions and weight of the device?",
    "What is the inlet pressure range, temperature range, and maximum ambient moisture the device can operate in?",
    "How long does it take for the device to perform a measurement?",
    "What is the accuracy of the SF6 volume percentage measurement?",
    "What is the measurement range and accuracy for SO2 concentration?",
    "How often should the device be calibrated to maintain its accuracy?",
    "What are the differences between the single, two-in-one, and three-in-one measuring devices for moisture, SF6, and SO2 measurements?",
    "What optional accessories are available for increasing pressure in medium voltage switchgear with a pressure of less than 0.2 bar?",
    "How can the external compressor and gas collecting bag be used with the device?",
    "Summarize the key physical and operational specifications of the MIRROR-ANALYSER SF6.",
    "Generate a detailed explanation of the measurement ranges and accuracy for moisture, SF6 volume percentage, and SO2 concentration.",
    "Describe the calibration requirements and intervals for the MIRROR-ANALYSER SF6.",
    "Compare the different models of the MIRROR-ANALYSER SF6 (e.g., 3-035R-R301, 3-035R-R302, 3-035R-R303).",
    "List the available accessories for increasing pressure in medium voltage switchgear and explain their use with the MIRROR-ANALYSER SF6.",
    "What kind of electronic device is housed inside the rugged carrying case, and what are its functions?"
]

# Function to process the question and get the answer
async def answer(question):
    relevant_docs = retriever_instance.similarity_search(question)
    context = ""
    relevant_images = []
    for d in relevant_docs:
        if d.metadata['type'] == 'text':
            context += '[text]' + d.metadata['original_content']
        elif d.metadata['type'] == 'table':
            context += '[table]' + d.metadata['original_content']
        elif d.metadata['type'] == 'image':
            context += '[image]' + d.page_content
            relevant_images.append(d.metadata['original_content'])
    
    chain = answer_prompt | load_model()
    result = await chain.ainvoke({'context': context, 'question': question})
    return result.content, relevant_images

# Function to decode base64 image strings and get image data
def get_image_data(base64_string):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue()

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome to DILO-CHATBOT Assistant! 🚀🤖\n\nHi there! 👋 I'm here to help you with information about our high-pressure application valve system and the MIRROR-ANALYSER SF6. You can choose from predefined questions or ask your own.").send()
    
    actions = [
        cl.Action(name="predefined", value="predefined", label="Choose a predefined question"),
        cl.Action(name="custom", value="custom", label="Ask your own question")
    ]
    await cl.Message(content="How would you like to proceed?", actions=actions).send()

@cl.action_callback("predefined")
async def on_predefined(action):
    question_list = "\n".join([f"{i+1}. {q}" for i, q in enumerate(predefined_questions)])
    await cl.Message(content=f"Please choose a question by entering its number:\n\n{question_list}").send()

@cl.action_callback("custom")
async def on_custom(action):
    await cl.AskUserMessage(content="Please enter your question:").send()

@cl.on_message
async def main(message: cl.Message):
    question = message.content
    try:
        question_index = int(question) - 1
        if 0 <= question_index < len(predefined_questions):
            question = predefined_questions[question_index]
    except ValueError:
        pass  # If not a number, treat as a custom question

    # Send a temporary message to show that we're processing
    msg = cl.Message(content="Thinking...")
    await msg.send()

    # Get the answer and relevant images
    text_answer, image_data_list = await answer(question)

    # Prepare the images
    elements = []
    for idx, img_data in enumerate(image_data_list):
        image_data = get_image_data(img_data)
        elements.append(cl.Image(name=f"image_{idx+1}", content=image_data, display="inline"))

    # Send the answer with images
    await cl.Message(content=text_answer, elements=elements).send()

    # Remove the temporary message
    await msg.remove()

    # Ask if the user wants to ask another question
    actions = [
        cl.Action(name="predefined", value="predefined", label="Choose another predefined question"),
        cl.Action(name="custom", value="custom", label="Ask another custom question"),
        cl.Action(name="end", value="end", label="End conversation")
    ]
    await cl.Message(content="Would you like to ask another question?", actions=actions).send()

@cl.action_callback("end")
async def on_end(action):
    await cl.Message(content="Thank you for using DILO-CHATBOT Assistant. Have a great day!").send()
    await cl.end()

if __name__ == "__main__":
    cl.run()