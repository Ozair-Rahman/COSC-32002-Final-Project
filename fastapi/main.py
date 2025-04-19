from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import PyPDF2
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import os

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index = faiss.IndexFlatL2(384)
chunks = []

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    else:
        return JSONResponse(content={"error": "Unsupported file type"}, status_code=400)

    # Chunking the text
    text_chunks = text.split('\n\n')  # Simple chunking by paragraphs
    for chunk in text_chunks:
        if chunk.strip():
            chunks.append(chunk.strip())
            vector = model.encode(chunk.strip())
            faiss_index.add(np.array([vector]))

    return {"message": "File processed", "num_chunks": len(chunks)}

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(request: QueryRequest):
    question_vector = model.encode(request.question)
    D, I = faiss_index.search(np.array([question_vector]), 5)  # Top 5 results
    retrieved_chunks = [chunks[i] for i in I[0]]
    
    return {"question": request.question, "retrieved_chunks": retrieved_chunks}

