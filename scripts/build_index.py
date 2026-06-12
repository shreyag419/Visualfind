import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import faiss
import numpy as np
import json
from backend.database import Database

def build_faiss_index():
    db = Database()
    products = db.get_all_products()
    
    print(f"Total products: {len(products)}")
    
    vectors = []
    product_ids = []
    
    for product in products:
        product_id   = product[0]
        image_vector = product[10]
        
        if image_vector is None:
            continue
        
        vec = np.array(json.loads(image_vector), dtype='float32')
        vectors.append(vec)
        product_ids.append(product_id)
    
    print(f"Products with vectors: {len(vectors)}")
    
    vectors_np = np.array(vectors).astype('float32')
    
    d = 512
    nlist = 100
    
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFPQ(quantizer, d, nlist, 8, 8)
    
    print("Training index...")
    index.train(vectors_np)
    
    print("Adding vectors to index...")
    index.add(vectors_np)
    
    print(f"Total vectors in index: {index.ntotal}")
    
    os.makedirs("indexes", exist_ok=True)
    faiss.write_index(index, "indexes/faiss_index.bin")
    np.save("indexes/id_map.npy", np.array(product_ids))
    
    print("Index saved to indexes/faiss_index.bin")
    print("ID map saved to indexes/id_map.npy")
    
    db.close()

if __name__ == "__main__":
    build_faiss_index()