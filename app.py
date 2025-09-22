import os
import streamlit as st
from dotenv import load_dotenv
from src.tools.pdf_ingest import build_index
from src.agent.agent_graph import run_agent


load_dotenv()


st.set_page_config(page_title="RL Copilot — LangGraph", page_icon="🤖", layout="wide")
st.title("RL Copilot: Your AI Assistant for Reinforcement Learning")

with st.expander("Build/Refresh PDF Index"):
    pdf_path = st.text_input("PDF path", value="data/rl_book.pdf")
    if st.button("Build index"):
        build_index(pdf_path)
        st.success("Index built.")

q = st.text_input("Ask an RL question…", value="Explain the Bellman optimality equation for Q* and its intuition.")
if st.button("Ask") and q:
    with st.spinner("Thinking…"):
        answer = run_agent(q)
    st.markdown(answer)