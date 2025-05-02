from typing import Dict, List
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

if __name__ == "__main__":
    data = load_preprocessing("eu_sousede.json")
    print(data["Finland"])