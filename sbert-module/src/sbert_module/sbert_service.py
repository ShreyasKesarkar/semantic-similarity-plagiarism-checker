import os
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

# Configuration paths
MODEL_NAME = 'all-MiniLM-L6-v2'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_MODEL_DIR = os.path.join(CURRENT_DIR, "models", MODEL_NAME)

# Global model instance for lazy loading
_model = None

def get_model() -> SentenceTransformer:
    """
    Lazy-loads the Sentence-BERT model.
    Checks if a local copy exists in sbert_module/models/all-MiniLM-L6-v2.
    If not, downloads it and saves a local copy for offline use.
    Automatically utilizes CUDA GPU if available.
    """
    global _model
    if _model is not None:
        return _model

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[SBERT] Loading model. Target device: {device.upper()}")

    if os.path.exists(LOCAL_MODEL_DIR):
        print(f"[SBERT] Loading model from local cache: {LOCAL_MODEL_DIR}")
        _model = SentenceTransformer(LOCAL_MODEL_DIR, device=device)
    else:
        print(f"[SBERT] Downloading model '{MODEL_NAME}' from Hugging Face...")
        _model = SentenceTransformer(MODEL_NAME, device=device)
        print(f"[SBERT] Saving model to local cache at: {LOCAL_MODEL_DIR}")
        os.makedirs(os.path.dirname(LOCAL_MODEL_DIR), exist_ok=True)
        _model.save(LOCAL_MODEL_DIR)

    return _model

def get_embeddings(texts: list[str]) -> np.ndarray:
    """
    Generates embeddings for a list of texts (sentences) in a single batch.
    
    Args:
        texts: A list of strings (sentences).
        
    Returns:
        A NumPy array of shape (N, 384) where N is the number of texts.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
        
    model = get_model()
    # By default model.encode returns a numpy array when convert_to_numpy=True
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

def get_embedding(text: str) -> np.ndarray:
    """
    Generates embedding for a single text. (Maintained for backward compatibility).
    """
    embeddings = get_embeddings([text])
    return embeddings[0]