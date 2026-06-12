import sqlite3
import json
import numpy as np
import os

class Database:
    def __init__(self, db_path="products.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                gender TEXT,
                master_category TEXT,
                sub_category TEXT,
                article_type TEXT,
                base_colour TEXT,
                season TEXT,
                usage TEXT,
                image_path TEXT,
                image_vector TEXT,
                text_vector TEXT
            )
        """)
        self.conn.commit()

    def insert_product(self, product: dict):
        self.conn.execute("""
            INSERT OR IGNORE INTO products 
            (id, name, gender, master_category, sub_category, 
             article_type, base_colour, season, usage, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product["id"],
            product["name"],
            product["gender"],
            product["master_category"],
            product["sub_category"],
            product["article_type"],
            product["base_colour"],
            product["season"],
            product["usage"],
            product["image_path"]
        ))
        self.conn.commit()

    def save_vectors(self, product_id: int, image_vector, text_vector):
        self.conn.execute("""
            UPDATE products
            SET image_vector = ?, text_vector = ?
            WHERE id = ?
        """, (
            json.dumps(image_vector.tolist()),
            json.dumps(text_vector.tolist()),
            product_id
        ))
        self.conn.commit()

    def get_all_products(self):
        cursor = self.conn.execute(
            "SELECT * FROM products"
        )
        return cursor.fetchall()

    def get_product_by_id(self, product_id: int):
        cursor = self.conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )
        return cursor.fetchone()

    def close(self):
        self.conn.close()