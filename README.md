# Chatbot LLM Backend

This repository contains the backend code for the **Chatbot LLM Backend** project. The backend is designed to power a chatbot that utilizes advanced language models (LLMs) for natural language processing and conversational AI capabilities.

## Features

- **Django Backend**: Robust and scalable backend framework for building web APIs and handling application logic.
- **LangChain Integration**: Efficiently integrates LLM functionalities such as:
  - Document retrieval
  - Contextual conversation handling
  - Customizable chatbot workflows
- **Chroma DB**: Used as the vector store for semantic search and storage of embeddings, ensuring fast and accurate document retrieval.

## Technology Stack

- **Backend Framework**: [Django](https://www.djangoproject.com/)
- **LLM and Chatbot Tools**: [LangChain](https://langchain-langchain.com/)
- **Vector Store Database**: [Chroma DB](https://www.trychroma.com/)

## Installation

To set up the backend locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/chatbot-llm-backend.git
   cd chatbot-llm-backend

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv\Scripts\activate

4. Install the dependencies
   ```bash
   pip install -r requirements.txt
   
6. Configure the database and environment variables.

   Update the .env file with necessary configurations (e.g., database credentials, API keys, etc.).
   
9. Run Migrations
   ```bash
   python manage.py migrate
   
11. Start the development server
    ```bash
    python manage.py runserver
