import os, json
import faiss, numpy as np
from sentence_transformers import SentenceTransformer


EMB_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


class PDFStore:
    def __init__(self, dir="index"):
        self.dir = dir
        self.index = faiss.read_index(os.path.join(dir, "pdf.index"))
        with open(os.path.join(dir, "meta.json"), encoding="utf-8") as f:
            self.meta = json.load(f)
        self.model = SentenceTransformer(EMB_MODEL_NAME)


    def search(self, query: str, k=6):
        q = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q, k)
        out = []
        for s, i in zip(scores[0], idxs[0]):
            rec = self.meta[int(i)]
            out.append({**rec, "score": float(s)})
        return out

    def read(self, ids):
        idset = set(ids)
        return [r for r in self.meta if r["id"] in idset]
