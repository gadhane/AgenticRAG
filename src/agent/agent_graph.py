
import os, json
from dotenv import load_dotenv
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from openai import OpenAI

from src.types.state import AgentState
from src.agent.prompts import (
    SYSTEM_PROMPT, PLANNER_PROMPT, SELF_CHECK_PROMPT,
    CITATION_INSTRUCTIONS, TRIPLE_EXTRACTION_PROMPT
)
from src.tools.pdf_store import PDFStore
from src.tools.web_tools import WebTools
from src.memory.graph_memory import GraphMemory

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

pdf = PDFStore("index")
web = WebTools()  # DuckDuckGo, no API key needed
kg = GraphMemory()

# ---------- LLM helper ----------

def chat(messages: List[dict], max_tokens=700):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

# ---------- Utility to update dict-state ----------

def update(state: AgentState, **kwargs) -> AgentState:
    new_state: AgentState = {**state}
    for k, v in kwargs.items():
        new_state[k] = v
    return new_state

# ---------- Nodes ----------

def plan_node(state: AgentState) -> AgentState:
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {state['question']}{PLANNER_PROMPT}"}
    ]
    plan = chat(msgs, max_tokens=250)
    subs = [s.lstrip("- ") for s in plan.splitlines() if s.strip()]
    return update(state, subqueries=subs[:3], hop=0)


def retrieve_pdf_node(state: AgentState) -> AgentState:
    hop = state.get("hop", 0)
    subs = state.get("subqueries", [])
    query = subs[hop] if subs and hop < len(subs) else state["question"]

    hits = pdf.search(query, k=6)
    ev = state.get("evidence_pdf", []) + hits

    # Graph memory expansions
    terms = [t for t in query.split() if len(t) > 2]
    expansions = kg.suggest_expansions(terms)
    for ex in expansions[:2]:
        ev += pdf.search(f"{query} {ex}", k=3)

    high = any(h.get("score", 0) >= 0.55 for h in hits)
    need_web = (not high) and (hop == 0)
    return update(state, evidence_pdf=ev, need_web=need_web)


def retrieve_web_node(state: AgentState) -> AgentState:
    hop = state.get("hop", 0)
    subs = state.get("subqueries", [])
    query = subs[hop] if subs and hop < len(subs) else state["question"]

    results = web.search(query, k=5)
    texts: List[Dict[str, Any]] = []
    for r in results[:3]:
        url = r.get("url")
        if not url: continue
        txt = web.read(url)
        if txt:
            texts.append({"url": url, "text": txt})
    return update(state, evidence_web=state.get("evidence_web", []) + texts, need_web=False)


def synthesize_node(state: AgentState) -> AgentState:
    pdf_bits = []
    for c in sorted(state.get("evidence_pdf", []), key=lambda x: -x.get("score", 0))[:6]:
        pdf_bits.append(f"[p.{c['page']}] {c['text'][:600]}")
    web_bits = []
    for w in state.get("evidence_web", [])[:2]:
        web_bits.append(f"[{w['url']}] {w['text'][:800]}")

    evidence = "\n\n".join(filter(None, ["\n".join(pdf_bits), "\n".join(web_bits)]))

    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
        f"Question: {state['question']}\n\nEvidence (PDF & Web):\n{evidence}\n\n"
        f"Draft an answer with citations. {CITATION_INSTRUCTIONS}"
        )}
        ]
    draft = chat(msgs, max_tokens=900)
    return update(state, draft=draft)

def self_check_node(state: AgentState) -> AgentState:
    # Ask the model if the draft is grounded in evidence
    msgs = [
        {"role": "system", "content": "You are a strict judge. Only answer YES or NO."},
        {"role": "user", "content": (
            f"Question: {state['question']}\n\n"
            f"Draft Answer:\n{state.get('draft','')}\n\n"
            "Is this answer fully supported by the evidence provided earlier? "
            "Reply with YES or NO only."
        )}
    ]
    verdict = chat(msgs, max_tokens=3).strip().upper()

    if verdict.startswith("YES"):
        # Keep the draft as final
        return update(state, final=state.get("draft", ""))
    else:
        # Ask the LLM to fix the draft using evidence
        msgs = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"Question: {state['question']}\n\n"
                f"Draft Answer:\n{state.get('draft','')}\n\n"
                "The draft is not fully supported. Revise it so that every claim is grounded "
                "in the evidence, and provide the improved final answer with citations."
            )}
        ]
        final = chat(msgs, max_tokens=700)
        return update(state, final=final)



def hop_or_finish_node(state: AgentState) -> AgentState:
    hop = state.get("hop", 0)
    more_hops = (hop + 1 < 3) and (len(state.get("evidence_web", [])) == 0) and (len(state.get("evidence_pdf", [])) < 3)
    if more_hops:
        return update(state, hop=hop + 1)
    return update(state, done=True)


def update_graph_memory_node(state: AgentState) -> AgentState:
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Answer: {state.get('final', '')}\n\n{TRIPLE_EXTRACTION_PROMPT}"}
    ]
    txt = chat(msgs, max_tokens=300)
    try:
        triples = json.loads(txt)
        if isinstance(triples, list):
            kg.add_triples([tuple(t) for t in triples if isinstance(t, list) and len(t) == 3])
    except Exception:
        pass
    return state

# ---------- Build Graph ----------

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("plan", plan_node)
    g.add_node("retrieve_pdf", retrieve_pdf_node)
    g.add_node("retrieve_web", retrieve_web_node)
    g.add_node("synthesize", synthesize_node)
    g.add_node("self_check", self_check_node)
    g.add_node("hop_or_finish", hop_or_finish_node)
    g.add_node("update_memory", update_graph_memory_node)

    g.set_entry_point("plan")

    g.add_edge("plan", "retrieve_pdf")
    g.add_conditional_edges(
        "retrieve_pdf",
        lambda s: "retrieve_web" if s.get("need_web") else "synthesize",
        {"retrieve_web": "retrieve_web", "synthesize": "synthesize"}
    )
    g.add_edge("retrieve_web", "synthesize")
    g.add_edge("synthesize", "self_check")
    g.add_edge("self_check", "hop_or_finish")
    g.add_conditional_edges(
        "hop_or_finish",
        lambda s: "retrieve_pdf" if not s.get("done") else "update_memory",
        {"retrieve_pdf": "retrieve_pdf", "update_memory": "update_memory"}
    )
    g.add_edge("update_memory", END)
    return g.compile()

# Convenience runner

def run_agent(question: str):
    graph = build_graph()
    init: AgentState = {"question": question, "subqueries": [], "hop": 0,
                        "evidence_pdf": [], "evidence_web": [], "draft": "",
                        "final": "", "need_web": False, "done": False}
    out = graph.invoke(init)
    # LangGraph returns a dict-like state (AddableValuesDict). Access keys directly.
    return out.get("final", "(No answer produced)")
