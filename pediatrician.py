from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import uvicorn

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("--- Incoming Request ---")
    print(f"Path: {request.url.path}")
    print(f"Method: {request.method}")
    print(f"Headers: {request.headers}")
    print("------------------------")
    response = await call_next(request)
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prepare vector DB and LLM once on startup
print("Preparing vector DB and LLM...")
vector_db_path = "./vector_db"
if os.path.exists(vector_db_path) and os.listdir(vector_db_path):
    vectordb = Chroma(persist_directory=vector_db_path, embedding_function=OllamaEmbeddings(model="llama3"))
else:
    loader = TextLoader("whattoexpectthefirstyear.txt", encoding="utf-8")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(model="llama3")
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=vector_db_path)
    vectordb.persist()

retriever = vectordb.as_retriever(search_kwargs={"k": 3})
llm = OllamaLLM(model="llama3")

template = """
You are a pediatrician. You will be provided with a context, which is an excerpt from the book "What to Expect the First Year".
Use this context to answer the question as accurately as possible.

If the context does not contain the answer, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""
prompt = PromptTemplate(input_variables=["context", "question"], template=template)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type_kwargs={"prompt": prompt})


class QuestionInput(BaseModel):
    question: str

class ContextInput(BaseModel):
    mia_context: Optional[str] = None
    luna_context: Optional[str] = None


@app.post("/add_context")
def add_context(input: ContextInput):
    texts_to_add = []
    if input.mia_context and input.mia_context.strip():
        texts_to_add.append(f"User-provided context for Mia: {input.mia_context}")
    if input.luna_context and input.luna_context.strip():
        texts_to_add.append(f"User-provided context for Luna: {input.luna_context}")

    if texts_to_add:
        vectordb.add_texts(texts_to_add)
        return {"message": "Context added successfully"}
    
    return {"message": "No new context provided"}

@app.post("/ask")
def ask_question(input: QuestionInput):
    result = qa_chain.invoke(input.question)
    return {"answer": result["result"]}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        forwarded_allow_ips='*'
    )
