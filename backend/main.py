import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import shutil
import uuid

from backend.search import hybrid_search
from backend.database import Database

app = FastAPI(
    title="VisualFind API",
    description="Multimodal fashion product search engine",
    version="1.0.0"
)

# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# serve product images as static files
app.mount("/images", StaticFiles(directory="data/raw/archive/images"), name="images")

# ─── Health Check ─────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "message": "VisualFind API is running"}


# ─── Text Search ──────────────────────────────────────
class TextSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    gender: Optional[str] = None  # ← add this

@app.post("/search/text")
def search_text(request: TextSearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = hybrid_search(
    query_text=request.query,
    top_k=request.top_k,
    gender=request.gender  # ← add this
)
    return {"query": request.query, "results": results}


# ─── Image Search ─────────────────────────────────────
@app.post("/search/image")
async def search_image(
    file: UploadFile = File(...),
    top_k: int = Form(default=10)
):
    # save uploaded image temporarily
    temp_path = f"temp_{uuid.uuid4().hex}.jpg"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        results = hybrid_search(
            query_image=temp_path,
            top_k=top_k
        )
        return {"results": results}
    
    finally:
        # always delete temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ─── Composed Search ──────────────────────────────────
@app.post("/search/composed")
async def search_composed(
    file: UploadFile = File(...),
    query: str = Form(...),
    image_weight: float = Form(default=0.7),
    top_k: int = Form(default=10)
):
    if not 0.0 <= image_weight <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="image_weight must be between 0.0 and 1.0"
        )
    
    temp_path = f"temp_{uuid.uuid4().hex}.jpg"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        results = hybrid_search(
            query_text=query,
            query_image=temp_path,
            image_weight=image_weight,
            top_k=top_k
        )
        return {
            "query": query,
            "image_weight": image_weight,
            "results": results
        }
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ─── Get Product by ID ────────────────────────────────
@app.get("/products/{product_id}")
def get_product(product_id: int):
    db = Database()
    product = db.get_product_by_id(product_id)
    db.close()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product[0],
        "name": product[1],
        "gender": product[2],
        "category": product[4],
        "article_type": product[5],
        "colour": product[6],
        "image_path": product[9]
    }