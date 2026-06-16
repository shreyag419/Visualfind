import os

import numpy as np
from PIL import Image

# heavy dependencies are imported lazily so importing this module
# doesn't fail immediately in environments without them
try:
    import torch
    import open_clip
    _HAS_TORCH = True
except Exception:
    torch = None
    open_clip = None
    _HAS_TORCH = False


MODEL_NAME = "ViT-B-32"
FINETUNED_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "clip_finetuned",
    "clip_finetuned.pt",
)

_model = None
_preprocess = None
_tokenizer = None
_device = None


def _load_model():
    global _model, _preprocess, _tokenizer, _device
    if not _HAS_TORCH:
        raise ImportError(
            "Missing optional dependencies: install 'torch' and 'open_clip' to use embeddings.\n"
            "Run: python -m pip install -r requirements.txt"
        )

    if _model is not None:
        return _model, _preprocess, _tokenizer, _device

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _model, _, _preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    _tokenizer = open_clip.get_tokenizer(MODEL_NAME)

    if os.path.exists(FINETUNED_MODEL_PATH):
        state = torch.load(FINETUNED_MODEL_PATH, map_location=_device)
        _model.load_state_dict(state)

    _model = _model.to(_device)
    _model.eval()
    return _model, _preprocess, _tokenizer, _device


def _normalize(vector):
    vector = vector.astype("float32")
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def encode_text(text):
    if not text:
        return None

    model, _, tokenizer, device = _load_model()
    tokens = tokenizer([text]).to(device)

    with torch.no_grad():
        features = model.encode_text(tokens)
        features = features.squeeze(0).detach().cpu().numpy()

    return _normalize(features)


def encode_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return None

    model, preprocess, _, device = _load_model()
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model.encode_image(image)
        features = features.squeeze(0).detach().cpu().numpy()

    return _normalize(features)
