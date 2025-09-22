

# Agentic RAG with LangGraph: RL Copilot
This project shows how to build an **Agentic RAG pipeline** using [LangGraph](https://www.langchain.com/langgraph), [FAISS](https://faiss.ai/), and [DuckDuckGo Search](https://duckduckgo.com/).  
The system is applied to *Reinforcement Learning: An Introduction* (Sutton & Barto) to answer questions grounded in the textbook, with web augmentation if the book is insufficient. You can put a book of your interst if you want.

---
## Features
- **PDF Ingestion**: Parse, chunk, and embed a textbook into FAISS for retrieval.
- **Multi-hop Planning**: LLM breaks down complex queries into sub-queries.
- **Dual Retrieval**: Search textbook first, fall back to DuckDuckGo if needed.
- **Synthesis**: Generate answers with inline citations to book pages and web links.
- **Self-Check**: Judge whether answers are evidence-grounded, revise if necessary.
- **Graph Memory**: Store knowledge triples to enrich future searches.
- **Streamlit UI**: Simple web interface to interact with the system.

---

## Installation
```bash
git clone https://github.com/your-username/agentic-rag-rl.git
cd agentic-rag-rl
pip install -r requirements.txt
````

Create a `.env` file with your OpenAI key:
```bash
OPENAI_API_KEY=sk-xxxx
OPENAI_MODEL=gpt-xx
# optional for web search keys
```

---
## Usage

### 1. Build the Index
Place your RL PDF (or any book) in `data/` and run:
```bash
python scripts/build_index.py --pdf data/reinforcement_learning.pdf --out index/
```

This creates:

* `index/pdf.index` → FAISS embeddings
* `index/meta.json` → chunk metadata

### 2. Run the Agent

Launch the Streamlit UI:

```bash
streamlit run app.py
```

Ask questions like:

* “Explain the Bellman optimality for Q and its intuition.”
* “What is the difference between value iteration and policy iteration?”

The system retrieves from the book, augments with web if needed, and returns a grounded answer with citations.

---

## Tutorial

Read the full step-by-step tutorial here:
👉 [Medium / Blog Link](https://your-blog-link.com)

---
## Contributing

Feel free to fork, open issues, or submit PRs to extend functionality (e.g., Neo4j memory backend, LaTeX rendering).

---

## License

MIT License © 2025

