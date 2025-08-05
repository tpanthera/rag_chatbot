import streamlit as st
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

# Set page configuration for the web app
st.set_page_config(page_title="Chat with Hemant's Resume", page_icon="📄")
st.title("📄 Chat with Hemant's Resume")
st.write("This app allows you to ask questions about Hemant Sadhwani's experience based on his resume.")

# --- RAG CHAIN INITIALIZATION ---

# This function will cache the RAG chain to avoid re-initializing it on every interaction
@st.cache_resource
def get_qa_chain():
    """Initializes and returns the RetrievalQA chain."""
    
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
    return qa_chain

# Get the initialized RAG chain
qa = get_qa_chain()

# --- CHAT INTERFACE ---

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages from the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input from the chat input box
if prompt := st.chat_input("Ask a question about Hemant's experience..."):
    # Add user's message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display a thinking spinner while processing
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Get the answer from the RAG chain
            response = qa.invoke(prompt)
            answer = response['result']
            st.markdown(answer)
    
    # Add the assistant's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})