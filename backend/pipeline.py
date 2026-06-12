import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Database

def load_data(csv_path: str, images_dir: str, categories: list = ["Apparel", "Footwear"]):
    
    print("Reading CSV...")
    df = pd.read_csv(csv_path, on_bad_lines='skip')
    
    print(f"Total products before filter: {len(df)}")
    
    # filter to only Apparel and Footwear
    df = df[df["masterCategory"].isin(categories)]
    
    print(f"Total products after filter: {len(df)}")
    
    # drop rows with missing values
    df = df.dropna(subset=["productDisplayName", "gender", 
                            "masterCategory", "subCategory",
                            "articleType", "baseColour"])
    
    print(f"Total products after cleaning: {len(df)}")
    
    db = Database()
    
    skipped = 0
    loaded = 0
    
    for _, row in df.iterrows():
        product_id = int(row["id"])
        image_path = os.path.join(images_dir, f"{product_id}.jpg")
        
        # skip if image doesn't exist
        if not os.path.exists(image_path):
            skipped += 1
            continue
        
        product = {
            "id": product_id,
            "name": str(row["productDisplayName"]),
            "gender": str(row["gender"]),
            "master_category": str(row["masterCategory"]),
            "sub_category": str(row["subCategory"]),
            "article_type": str(row["articleType"]),
            "base_colour": str(row["baseColour"]),
            "season": str(row.get("season", "")),
            "usage": str(row.get("usage", "")),
            "image_path": image_path
        }
        
        db.insert_product(product)
        loaded += 1
    
    print(f"Loaded: {loaded} products")
    print(f"Skipped: {skipped} products (missing images)")
    
    db.close()
    print("Done.")

if __name__ == "__main__":
    load_data(
        csv_path="data/raw/archive/styles.csv",
        images_dir="data/raw/archive/images"
    )