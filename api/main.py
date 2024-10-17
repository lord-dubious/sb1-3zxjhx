import streamlit as st
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langchain.document_loaders import PyPDFLoader, TextLoader, GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ollama
ollama = Ollama(base_url=os.getenv("OLLAMA_BASE_URL"), model=os.getenv("OLLAMA_MODEL"))

# Initialize embeddings and vector store
embeddings = HuggingFaceEmbeddings()
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Initialize retrieval chain
retriever = vector_store.as_retriever()
qa_chain = RetrievalQA.from_chain_type(llm=ollama, chain_type="stuff", retriever=retriever)

class GenerateRequest(BaseModel):
    prompt: str

class RepoRequest(BaseModel):
    url: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Process the file based on its type
    if file.filename.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Add documents to the vector store
    vector_store.add_documents(texts)
    
    return {"message": "File processed and added to the knowledge base"}

@app.post("/generate")
async def generate_code(request: GenerateRequest):
    prompt = request.prompt
    response = qa_chain.run(prompt)
    return {"generated_code": response}

@app.post("/add_repo")
async def add_repo(request: RepoRequest):
    repo_url = request.url
    repo_path = f"repos/{repo_url.split('/')[-1]}"
    
    # Clone the repository
    os.system(f"git clone {repo_url} {repo_path}")
    
    # Load the repository contents
    loader = GitLoader(repo_path=repo_path, branch="main")
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Add documents to the vector store
    vector_store.add_documents(texts)
    
    # Clean up: remove the cloned repository
    os.system(f"rm -rf {repo_path}")
    
    return {"message": "Repository processed and added to the knowledge base"}

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("repos"):
        os.makedirs("repos")
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Streamlit UI
st.title("Ollama RAG App")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    st.write("File uploaded successfully!")

repo_url = st.text_input("Enter Git repository URL")
if st.button("Add Repository"):
    if repo_url:
        # Call the add_repo endpoint
        import requests
        response = requests.post("http://localhost:8000/add_repo", json={"url": repo_url})
        if response.status_code == 200:
            st.success("Repository added successfully!")
        else:
            st.error("Failed to add repository")

user_input = st.text_area("Enter your prompt")
if st.button("Generate Code"):
    if user_input:
        response = qa_chain.run(user_input)
        st.code(response)
    else:
        st.warning("Please enter a prompt.")