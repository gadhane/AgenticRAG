import networkx as nx
from typing import List, Tuple


class GraphMemory:
    def __init__(self):
        self.g = nx.MultiDiGraph()


    def add_triples(self, triples: List[Tuple[str, str, str]]):
        for h, r, t in triples:
            self.g.add_node(h, type="entity")
            self.g.add_node(t, type="entity")
            self.g.add_edge(h, t, label=r)


    def neighbors(self, entity: str, max_deg: int = 2):
        if entity not in self.g: return []
        nbrs = set()
        for _, v, _ in self.g.out_edges(entity, data=True):
            nbrs.add(v)
        return list(nbrs)[:max_deg]


    def suggest_expansions(self, query_terms: List[str]):
        expansions = set()
        for term in query_terms:
            expansions.update(self.neighbors(term))
        return list(expansions)