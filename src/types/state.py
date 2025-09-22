from typing import List, Dict, Any, TypedDict


# LangGraph works best with dict-like states (TypedDict). Avoid Pydantic models here.
class AgentState(TypedDict, total=False):
    question: str
    subqueries: List[str]
    hop: int
    evidence_pdf: List[Dict[str, Any]]
    evidence_web: List[Dict[str, Any]]
    draft: str
    final: str
    need_web: bool
    done: bool