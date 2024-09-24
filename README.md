# Multi-Model-RAG

Multi-Model Retrieval Augmented Generation (RAG) for PDF data processing and analysis.

## Overview

This application processes PDF documents containing text, images, and tables to perform multi-modal retrieval and argument generation. It utilizes unstructured.io for PDF data extraction, CromaDB for vector data storage, OpenAI's embedding model for creating embeddings, and Chainlit for the chat user interface.

# Complete Workflow for Multi-Model-RAG

This document outlines the entire process flow for the Multi-Model Retrieval Augmented Generation (RAG) system, from data ingestion to user interaction.

## 1. Data Ingestion and Processing

### 1.1 PDF Upload
- User uploads a PDF document containing text, images, and tables.
- The system saves the PDF to a designated input directory.

### 1.2 PDF Processing (process_pdfs.py)
- Utilize unstructured.io API to extract content from the PDF:
  - Text extraction
  - Image extraction
  - Table extraction
- Store extracted data in a structured format (e.g., JSON) for further processing.

### 1.3 Image Processing (image_processing.py)
- For each extracted image:
  - Perform preprocessing (resize, normalize, etc.)
  - Generate image embeddings using a pre-trained model (e.g., CLIP)
  - Store image embeddings for later retrieval

## 2. Data Indexing and Storage

### 2.1 Text Embedding Generation
- For each chunk of extracted text:
  - Generate embeddings using OpenAI's text embedding model
  - Store text content and its embedding

### 2.2 Table Processing
- For each extracted table:
  - Convert table to a textual representation
  - Generate embeddings for the textual representation
  - Store table content and its embedding

### 2.3 CromaDB Integration (retriver.py)
- Initialize CromaDB client
- Create collections for different types of data (text, images, tables)
- Insert all generated embeddings and their associated content into appropriate CromaDB collections

## 3. Retrieval System Setup

### 3.1 Similarity Search Implementation (retriver.py)
- Implement functions to perform similarity search on CromaDB collections
- Create methods to combine results from different modalities (text, images, tables)

### 3.2 Query Processing
- Implement query preprocessing to handle different types of user queries
- Create a pipeline to generate embeddings for user queries

## 4. Language Model Integration (llms.py)

### 4.1 Model Setup
- Initialize the chosen language model (e.g., GPT-3.5 or GPT-4)
- Set up API connections and handle authentication

### 4.2 Prompt Engineering
- Design prompts that effectively utilize retrieved information
- Implement dynamic prompt generation based on query type and retrieved context

## 5. Application Setup (app2.py)

### 5.1 Chainlit UI Integration
- Set up Chainlit application structure
- Design the user interface for file upload and chat interaction

### 5.2 Application Logic
- Implement the main application loop:
  1. Receive user query
  2. Process query and perform similarity search
  3. Retrieve relevant information from CromaDB
  4. Generate LLM prompt with retrieved context
  5. Get LLM response
  6. Display response to user via Chainlit UI

## 6. Deployment

### 6.1 Docker Configuration
- Create Dockerfile:
  - Set up Python environment
  - Install dependencies
  - Copy application files
  - Set entry point

### 6.2 Docker Compose Setup
- Create docker-compose.yml:
  - Define services (app, database if needed)
  - Set environment variables
  - Configure volumes and ports

### 6.3 Deployment Steps
1. Build Docker image:
   ```
   docker build -t multi-model-rag .
   ```
2. Run with Docker Compose:
   ```
   docker-compose up --build
   ```

## 7. User Interaction

1. User accesses the application via web browser (http://localhost:8000)
2. Store PDF Dcument Data in Data folder
3. System processes the PDF (steps 1-2)
4. User enters a query in the chat interface
5. System processes query, retrieves information, and generates a response (steps 3-5)
6. User receives the response and can ask follow-up questions

## Features

- PDF processing (text, images, tables)
- Multi-modal data extraction using unstructured.io
- Vector storage with CromaDB
- Embedding generation using OpenAI's API
- Similarity search for relevant information retrieval
- Interactive chat interface powered by Chainlit

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Multi-Model-RAG.git
   cd Multi-Model-RAG
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   UNSTRUCTURED_API_KEY=your_unstructured_io_api_key
   ```

## Usage

1. Start the application:
   ```
   python app2.py
   ```

2. Open your web browser and navigate to `http://localhost:8000` to access the Chainlit UI.

3. Upload a PDF file and start interacting with the chatbot to retrieve information and generate arguments based on the content.

## File Structure

- `app2.py`: Main application file
- `image_processing.py`: Handles image extraction and processing
- `process_pdfs.py`: PDF processing and data extraction
- `retriver.py`: Implements retrieval logic and similarity search
- `llms.py`: Language model integration for text generation
- `Dockerfile`: Docker configuration for containerization
- `docker-compose.yml`: Docker Compose configuration for easy deployment

## Development

To contribute to this project:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Submit a pull request with a clear description of your improvements

## Setup With Docker 

This application can be easily deployed using Docker, which ensures consistency across different environments and simplifies the setup process.

### Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

### Building and Running with Docker

1. Build the Docker image:
   ```
   docker build -t multi-model-rag .
   ```
   This command builds a Docker image named `multi-model-rag` based on the instructions in the `Dockerfile`.

2. Run the container:
   ```
   docker run -p 8000:8000 -e OPENAI_API_KEY=your_openai_api_key -e UNSTRUCTURED_API_KEY=your_unstructured_io_api_key multi-model-rag
   ```
   This command starts a container from the `multi-model-rag` image, maps port 8000 from the container to your host machine, and sets the necessary environment variables.

### Using Docker Compose

For a more streamlined setup, especially when dealing with multiple services or environment variables, you can use Docker Compose:

1. Ensure your `docker-compose.yml` file is properly configured. It should look something like this:

   ```yaml
   version: '3'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - UNSTRUCTURED_API_KEY=${UNSTRUCTURED_API_KEY}
       volumes:
         - ./data:/app/data
   ```

2. Create a `.env` file in the same directory as your `docker-compose.yml` with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   UNSTRUCTURED_API_KEY=your_unstructured_io_api_key
   ```

3. Run the application using Docker Compose:
   ```
   docker-compose up --build
   ```
   This command builds the image if it doesn't exist, creates the container, and starts the application.

### Accessing the Application

Once the Docker container is running, you can access the Chainlit UI by opening a web browser and navigating to `http://localhost:8000`.

### Managing Docker Containers

- To stop the container, press `Ctrl+C` in the terminal where it's running.
- To run the container in detached mode (in the background):
  ```
  docker-compose up -d
  ```
- To stop and remove the containers:
  ```
  docker-compose down
  ```
- To view logs of a detached container:
  ```
  docker-compose logs -f
  ```

### Troubleshooting

- If you encounter permission issues with the data volume, you may need to adjust the permissions on your host machine or use a named volume in the `docker-compose.yml` file.
- Ensure that the ports specified in the `Dockerfile`, `docker-compose.yml`, and the application code all match.
- If you make changes to the code, remember to rebuild the Docker image for the changes to take effect.

By using Docker, you ensure that the application runs in a consistent environment, making it easier to deploy and share with others. It also simplifies the process of managing dependencies and environment variables.



## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [unstructured.io](https://unstructured.io/) for PDF data extraction
- [CromaDB](https://www.trychroma.com/) for vector storage
- [OpenAI](https://openai.com/) for embedding model
- [Chainlit](https://github.com/chainlit/chainlit) for the chat UI

## Contact

For any questions or support, please open an issue in the GitHub repository.
