from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from pinecone import Pinecone

# --- APPLICATION SETUP ---

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow our React app to call this API
CORS(app)

# --- RAG CHAIN INITIALIZATION ---

# This function will initialize the RAG chain once and reuse it for all requests
# Using a global variable to hold the chain after first initialization
qa_chain = None

def initialize_qa_chain():
    """Initializes and returns the RetrievalQA chain."""
    global qa_chain
    if qa_chain is not None:
        return qa_chain
        
    print("Initializing RAG chain...")
    # Load API keys from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    # Initialize Pinecone and embeddings
    pc = Pinecone(api_key=PINECONE_API_KEY)
    embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
    index_name = "pdf-index" # The name of your Pinecone index

    # Connect to the existing Pinecone index
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding
    )

    # Initialize the LLM
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name='gpt-4o',
        temperature=0.0
    )

    # Define the prompt template
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Provide a concise answer in 1-4 sentences:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Create the RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": PROMPT}
    )
    print("RAG chain initialized successfully.")
    return qa_chain

# --- API ENDPOINT ---

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles chat requests from the frontend."""
    try:
        # Get the user's prompt from the request body
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Get the answer from the RAG chain
        chain = initialize_qa_chain()
        response = chain.invoke(prompt)
        answer = response.get('result', "Sorry, I couldn't find an answer.")
        
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

# --- RUN THE APP ---

if __name__ == '__main__':
    # Initialize the chain on startup
    initialize_qa_chain()
    # Runs the Flask app on localhost, port 5000
    app.run(host='0.0.0.0', port=5000)