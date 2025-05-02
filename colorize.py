from typing import Dict, List, Iterable
from diktyonphi import Graph, GraphType
import json

def load_preprocessing(filename: str) -> Dict[str, List[str]]:
    with open(filename, "rt") as f:
        data = json.load(f)

    for state in data.keys():
        data[state] = [neighbour for neighbour in data[state]
                       if neighbour in data]
    return data

def make_graph(data: Dict[str, List[str]]) -> Graph:
    g = Graph(GraphType.UNDIRECTED)
    for state in data.keys():
        node = g.add_node(state)
        node["color"] = None

    for state in data.keys():
        for neighbour in data[state]:
            if not g.node(state).is_edge_to(neighbour):
                g.add_edge(state, neighbour)
    return g


def get_max_degree_node(g: Graph, nodes: Iterable[str]) -> str:
    return max(nodes, key=lambda state: g.node(state).out_degree)

def colorize(g: Graph):
    colorless = set(g.node_ids())
    while colorless:
        print(colorless)
        next_state = get_max_degree_node(g, colorless)
        print(next_state)


if __name__ == "__main__":
    data = load_preprocessing("eu_sousede.json")
    g = make_graph(data)
    # g.export_to_png("eu_sousede.png")
    colorize(g)


