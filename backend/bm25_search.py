import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import numpy as np
from rank_bm25 import BM25Okapi
from backend.database import Database

def build_bm25_index():
    db = Database()
    products = db.get_all_products()
    
    descriptions = []
    product_ids = []
    
    for product in products:
        product_id = product[0]
        name       = product[1]
        article    = product[5]
        colour     = product[6]
        usage      = product[8]
        
        text = f"{name} {article} {colour} {usage}"
        descriptions.append(text.lower().split())
        product_ids.append(product_id)
    
    bm25 = BM25Okapi(descriptions)
    
    os.makedirs("indexes", exist_ok=True)
    with open("indexes/bm25_index.pkl", "wb") as f:
        pickle.dump({
            "bm25": bm25,
            "product_ids": product_ids
        }, f)
    
    print(f"BM25 index built for {len(product_ids)} products")
    db.close()

def load_bm25_index():
    with open("indexes/bm25_index.pkl", "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":
    build_bm25_index()