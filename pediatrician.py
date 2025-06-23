"""
AI Pediatrician Backend

A FastAPI application that provides pediatric advice using LangChain and Ollama.
The system uses "What to Expect the First Year" book as knowledge base and allows
users to add personal context about their children.
"""

import os
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

import uvicorn

# Configuration constants
VECTOR_DB_PATH = "./vector_db"
KNOWLEDGE_BASE_FILE = "whattoexpectthefirstyear.txt"
OLLAMA_MODEL = "llama3"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_K = 3
HOST = "0.0.0.0"
PORT = 8000

# Pydantic models for API requests
class QuestionInput(BaseModel):
    """Model for question input."""
    question: str

class ContextInput(BaseModel):
    """Model for context input about children."""
    mia_context: Optional[str] = None
    luna_context: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="AI Pediatrician API",
    description="An AI-powered pediatrician that provides advice based on 'What to Expect the First Year'",
    version="1.0.0"
)

def setup_cors() -> None:
    """Configure CORS middleware for the application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # For dev only - test for specific host in future
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_logging_middleware() -> None:
    """Add logging middleware to track incoming requests."""
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        print("--- Incoming Request ---")
        print(f"Path: {request.url.path}")
        print(f"Method: {request.method}")
        print("------------------------")
        response = await call_next(request)
        return response

def load_knowledge_base() -> Chroma:
    """
    Load or create the vector database from the knowledge base file.
    
    Returns:
        Chroma: The initialized vector database
    """
    print("Preparing vector DB and LLM...")
    
    # Check if vector database already exists
    if os.path.exists(VECTOR_DB_PATH) and os.listdir(VECTOR_DB_PATH):
        print("Loading existing vector database...")
        return Chroma(
            persist_directory=VECTOR_DB_PATH, 
            embedding_function=OllamaEmbeddings(model=OLLAMA_MODEL)
        )
    
    # Create new vector database from knowledge base file
    print("Creating new vector database from knowledge base...")
    loader = TextLoader(KNOWLEDGE_BASE_FILE, encoding="utf-8")
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)

    # Create embeddings and vector database
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
    vectordb = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=VECTOR_DB_PATH
    )
    vectordb.persist()
    
    print("Vector database created successfully!")
    return vectordb

def create_qa_chain(vectordb: Chroma) -> RetrievalQA:
    """
    Create the question-answering chain with the pediatrician prompt.
    
    Args:
        vectordb: The vector database for retrieval
        
    Returns:
        RetrievalQA: The configured QA chain
    """
    # Create retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": RETRIEVER_K})
    
    # Initialize LLM
    llm = OllamaLLM(model=OLLAMA_MODEL)
    
    # Define the pediatrician prompt template
    template = """
    You are a pediatrician. You will be provided with a context, which is an excerpt 
    from the book "What to Expect the First Year". Use this context to answer the 
    question as accurately as possible.

    If the context does not contain the answer, say "I don't know".

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    
    prompt = PromptTemplate(
        input_variables=["context", "question"], 
        template=template
    )
    
    return RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=retriever, 
        chain_type_kwargs={"prompt": prompt}
    )

def add_context_to_database(context_input: ContextInput) -> List[str]:
    """
    Add user-provided context to the vector database.
    
    Args:
        context_input: The context input containing information about children
        
    Returns:
        List[str]: List of texts that were added to the database
    """
    texts_to_add = []
    
    if context_input.mia_context and context_input.mia_context.strip():
        texts_to_add.append(f"User-provided context for Mia: {context_input.mia_context}")
    
    if context_input.luna_context and context_input.luna_context.strip():
        texts_to_add.append(f"User-provided context for Luna: {context_input.luna_context}")
    
    return texts_to_add

# Initialize application components
setup_cors()
setup_logging_middleware()

# Load vector database and create QA chain
vectordb = load_knowledge_base()
qa_chain = create_qa_chain(vectordb)

@app.post("/add_context")
def add_context(input: ContextInput):
    """
    Add context about children to the knowledge base.
    
    Args:
        input: ContextInput containing information about Mia and/or Luna
        
    Returns:
        dict: Success or error message
    """
    texts_to_add = add_context_to_database(input)
    
    if texts_to_add:
        vectordb.add_texts(texts_to_add)
        return {"message": "Context added successfully"}
    
    return {"message": "No new context provided"}

@app.post("/ask")
def ask_question(input: QuestionInput):
    """
    Ask a question to the AI pediatrician.
    
    Args:
        input: QuestionInput containing the user's question
        
    Returns:
        dict: The AI pediatrician's answer
    """
    result = qa_chain.invoke(input.question)
    return {"answer": result["result"]}

if __name__ == "__main__":
    print(f"Starting AI Pediatrician on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        proxy_headers=True,
        forwarded_allow_ips='*'
    )
