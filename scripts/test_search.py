import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import faiss
import numpy as np
from backend.database import Database
from backend.embeddings import encode_text, encode_image

def search(query_text=None, query_image=None, top_k=5):
    index = faiss.read_index("indexes/faiss_index.bin")
    id_map = np.load("indexes/id_map.npy")
    
    if query_text:
        query_vector = encode_text(query_text)
    elif query_image:
        query_vector = encode_image(query_image)
    else:
        print("Provide text or image")
        return
    
    query_vector = query_vector.reshape(1, -1).astype('float32')
    
    index.nprobe = 10
    distances, indices = index.search(query_vector, top_k)
    
    db = Database()
    print(f"\nTop {top_k} results:\n")
    
    for i, idx in enumerate(indices[0]):
        product_id = id_map[idx]
        product = db.get_product_by_id(int(product_id))
        if product:
            print(f"{i+1}. {product[1]}")
            print(f"   Category: {product[4]} | Colour: {product[6]}")
            print(f"   Image: {product[9]}")
            print()
    
    db.close()

if __name__ == "__main__":
    search(query_text="formal black shoes for men")