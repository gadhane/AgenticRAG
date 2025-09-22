import os, json, uuid
import fitz # pip install PyMuPDF
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss # pip install faiss-cpu
import numpy as np


EMB_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


def chunk_text(text, chunk_size=1000, overlap=200):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        if not chunk: break
        chunks.append(" ".join(chunk))
        i += max(1, chunk_size - overlap)
    return chunks


def build_index(pdf_path: str, out_dir="index", chunk_size=1000, overlap=200):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    records = []
    for i in tqdm(range(len(doc)), desc="Extracting & chunking"):
        page_no = i + 1
        text = doc[i].get_text("text")
        for chunk in chunk_text(text, chunk_size, overlap):
            rid = str(uuid.uuid4())
            records.append({"id": rid, "text": chunk, "page": page_no, "source": "pdf"})


    model = SentenceTransformer(EMB_MODEL_NAME)
    embs = model.encode([r["text"] for r in records], normalize_embeddings=True, show_progress_bar=True)
    embs = np.array(embs, dtype="float32")
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)


    faiss.write_index(index, os.path.join(out_dir, "pdf.index"))
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)
    print(f"Indexed {len(records)} chunks → {out_dir}")