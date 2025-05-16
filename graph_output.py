import sys
from io import StringIO

from diktyonphi import Graph, Edge, Node, GraphType
from typing import TextIO

class Serializer:
    def __init__(self, graph:Graph):
        self._graph = graph

    def serialize(self, output: TextIO):
        self.write_header(output)
        self.write_nodes(output)
        self.write_edges(output)
        self.write_foot(output)

    def write_header(self, output: TextIO):
        pass

    def write_nodes(self, output: TextIO):
        for i, node in  enumerate(self._graph):
            self.write_node(i, node, output)

    def write_edges(self, output: TextIO):
        for node in self._graph:
            for target in node.neighbor_nodes:
                if (self._graph.type == GraphType.DIRECTED
                        or node.id < target.id):
                    # funguje jen, když node id je kromě hashable i orderable (<)
                    self.write_edge(node.to(target), output)

    def write_foot(self, output: TextIO):
        pass

    def write_node(self, i: int, node: Node, output: TextIO):
        raise NotImplemented("abstract method")

    def write_edge(self, edge: Edge, output: TextIO):
        raise NotImplemented("abstract method")

class EdgeListSerializer(Serializer):
    def __init__(self, graph:Graph):
        super().__init__(graph)

    def write_node(self, i: int, node: Node, output: TextIO):
        pass

    def write_edge(self, edge: Edge, output: TextIO):
        output.write(f'"{edge.src.id}" "{edge.dest.id}"\n')

class AdjacencyListSerializer(Serializer):
    def __init__(self, graph:Graph):
        super().__init__(graph)

    def write_header(self, output: TextIO):
        pass

    def write_node(self, i: int, node: Node, output: TextIO):
        pass

class DotSerializer(Serializer):
    def __init__(self, graph:Graph):
        super().__init__(graph)

    def write_header(self, output: TextIO):
        pass
    def write_node(self, i: int, node: Node, output: TextIO):
        pass
    def write_edge(self, edge: Edge, output: TextIO):
        pass
    def write_foot(self, output: TextIO):
        pass


g = Graph(GraphType.UNDIRECTED)
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 2)

serializer = EdgeListSerializer(g)
# with open("myhraph.txt", "wt") as f:
#    serializer.serialize(f)

#serializer.serialize(sys.stdout)

with StringIO() as sf:
    serializer.serialize(sf)
    text = sf.getvalue()

print(text)


