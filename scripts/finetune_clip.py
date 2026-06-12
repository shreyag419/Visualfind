import torch
import open_clip
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import pandas as pd
import numpy as np
import os

class FashionDataset(Dataset):
    def __init__(self, csv_path, images_dir, preprocess, categories=["Apparel", "Footwear"]):
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        df = df[df["masterCategory"].isin(categories)]
        df = df.dropna(subset=["productDisplayName", "gender",
                                "masterCategory", "subCategory",
                                "articleType", "baseColour"])
        
        df["image_path"] = df["id"].apply(
            lambda x: os.path.join(images_dir, f"{x}.jpg")
        )
        df = df[df["image_path"].apply(os.path.exists)]
        self.df = df.reset_index(drop=True)
        self.preprocess = preprocess
        print(f"Dataset size: {len(self.df)}")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        image = self.preprocess(
            Image.open(row["image_path"]).convert("RGB")
        )
        
        text = (f"{row['productDisplayName']} "
                f"{row['articleType']} "
                f"{row['baseColour']} "
                f"{row['gender']} "
                f"{row['usage'] if pd.notna(row.get('usage')) else ''}")
        
        return image, text


def contrastive_loss(image_features, text_features, temperature=0.07):
    image_features = F.normalize(image_features, dim=-1)
    text_features  = F.normalize(text_features,  dim=-1)
    
    logits = (image_features @ text_features.T) / temperature
    labels = torch.arange(len(image_features)).to(logits.device)
    
    loss_i = F.cross_entropy(logits,   labels)
    loss_t = F.cross_entropy(logits.T, labels)
    return (loss_i + loss_t) / 2


def train(csv_path, images_dir, output_dir, epochs=3, batch_size=32, lr=1e-5):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32')
    tokenizer = open_clip.get_tokenizer('ViT-B-32')
    model = model.to(device)

    dataset = FashionDataset(csv_path, images_dir, preprocess)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=2)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        batches = 0
        
        for images, texts in dataloader:
            images = images.to(device)
            tokens = tokenizer(texts).to(device)

            image_features = model.encode_image(images)
            text_features  = model.encode_text(tokens)

            loss = contrastive_loss(image_features, text_features)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            batches += 1

            if batches % 50 == 0:
                print(f"Epoch {epoch+1} | Batch {batches} | Loss: {loss.item():.4f}")

        avg_loss = total_loss / batches
        print(f"Epoch {epoch+1} complete | Avg Loss: {avg_loss:.4f}")

    os.makedirs(output_dir, exist_ok=True)
    torch.save(model.state_dict(), f"{output_dir}/clip_finetuned.pt")
    print(f"Model saved to {output_dir}/clip_finetuned.pt")


if __name__ == "__main__":
    train(
        csv_path="/kaggle/input/datasets/paramaggarwal/fashion-product-images-small/styles.csv",
        images_dir="/kaggle/input/datasets/paramaggarwal/fashion-product-images-small/images",
        output_dir="/kaggle/working/models"
    )