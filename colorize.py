from typing import Dict, List, Iterable
from diktyonphi import Graph, GraphType
import json

class ColorGraph(Graph):
    PALETTE = ["blue", "red", "green", "yellow", "orange", "purple", "pink"]
    def __init__(self, type: GraphType):
        super().__init__(type)
    def to_dot(self, label_attr:str ="label", weight_attr:str = "weight") -> str:
        #TODO převezmete kód z Graph a změníte
        # lines.append(f'    "{node_id}" [label="{label}"];')
        lines = []
        name = "G"
        connector = "->" if self.type == GraphType.DIRECTED else "--"

        lines.append(f'digraph {name} {{' if self.type == GraphType.DIRECTED else f'graph {name} {{')

        # Nodes
        for node_id in self.node_ids():
            node = self.node(node_id)
            label = node[label_attr] if label_attr in node._attrs else str(node_id)
            lines.append(f'''    "{node_id}" [label="{label}",style=filled, 
                                 fillcolor={ColorGraph.PALETTE[node['color']]}];''')

        # Edges
        seen = set()
        for node_id in self.node_ids():
            node = self.node(node_id)
            for dst_id in node.neighbor_ids:
                if self.type == GraphType.UNDIRECTED and (dst_id, node_id) in seen:
                    continue
                seen.add((node_id, dst_id))
                edge = node.to(dst_id)
                label = edge[weight_attr] if weight_attr in edge._attrs else ""
                lines.append(f'    "{node_id}" {connector} "{dst_id}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)


def load_preprocessing(filename: str) -> Dict[str, List[str]]:
    with open(filename, "rt") as f:
        data = json.load(f)

    for state in data.keys():
        data[state] = [neighbour for neighbour in data[state]
                       if neighbour in data]
    return data

def make_graph(data: Dict[str, List[str]]) -> Graph:
    g = ColorGraph(GraphType.UNDIRECTED)
    for state in data.keys():
        node = g.add_node(state)
        node["color"] = None

    for state in data.keys():
        for neighbour in data[state]:
            if not g.node(state).is_edge_to(neighbour):
                g.add_edge(state, neighbour)
    return g

#FIXME: možná příliš brutal force
def first_not_used(colors: Iterable[int]) -> int:
    for i in range(len(colors) + 1):
        if i not in colors:
            return i

def get_max_degree_node(g: Graph, nodes: Iterable[str]) -> str:
    return max(nodes, key=lambda state: g.node(state).out_degree)

def set_node_color(g: Graph, node: str) -> None:
    color_of_neighbours = [neighbour_node["color"]  for neighbour_node
                             in g.node(node).neighbor_nodes]
    g.node(node)["color"] = first_not_used(color_of_neighbours)

def colorize(g: Graph):
    colorless = set(g.node_ids())
    while colorless:
        print(colorless)
        next_state = get_max_degree_node(g, colorless)
        set_node_color(g, next_state)
        print(next_state, g.node(next_state)["color"])
        colorless.remove(next_state)

if __name__ == "__main__":
    data = load_preprocessing("eu_sousede.json")
    g = make_graph(data)
    colorize(g)
    g.export_to_png("eu_sousede.png")


