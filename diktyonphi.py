import enum
import subprocess
from typing import Dict, Hashable, Any, Optional, Iterator


class GraphType(enum.Enum):
    """Graph orientation type: directed or undirected."""
    DIRECTED = 0
    UNDIRECTED = 1


class Edge:
    """Representation of an edge between two nodes with associated attributes."""

    def __init__(self, src_id: Hashable, dest_id: Hashable, attrs: Dict[str, Any]):
        """
        Initialize an edge from src_id to dest_id with given attributes.

        :param src_id: Source node identifier.
        :param dest_id: Destination node identifier.
        :param attrs: Dictionary of edge attributes.
        """
        self.src_id = src_id
        self.dest_id = dest_id
        self._attrs = attrs

    def __getitem__(self, key: str) -> Any:
        """Access edge attribute by key."""
        return self._attrs[key]

    def __setitem__(self, key: str, val: Any) -> None:
        """Set edge attribute by key."""
        self._attrs[key] = val

    def __repr__(self):
        return f"Edge({self.src_id}→{self.dest_id}, {self._attrs})"


class Node:
    """Representation of a graph node with attributes and outgoing edges."""

    def __init__(self, node_id: Hashable, attrs: Dict[str, Any]):
        """
        Initialize a node with a given identifier and attributes.

        :param node_id: Unique identifier of the node.
        :param attrs: Dictionary of node attributes.
        """
        self.id = node_id
        self._attrs = attrs
        self._neighbors: Dict[Hashable, Dict[str, Any]] = {}

    def __getitem__(self, item: str) -> Any:
        """Access node attribute by key."""
        return self._attrs[item]

    def __setitem__(self, item: str, val: Any) -> None:
        """Set node attribute by key."""
        self._attrs[item] = val

    def to(self, dest_id: Hashable) -> Edge:
        """
        Get the edge from this node to the specified destination node.

        :param dest_id: ID of the target node.
        :return: Edge instance representing the connection.
        :raises ValueError: If no such edge exists.
        """
        if dest_id not in self._neighbors:
            raise ValueError(f"No edge from {self.id} to {dest_id}")
        return Edge(self.id, dest_id, self._neighbors[dest_id])

    def connected_to(self, dest_id: Hashable) -> bool:
        """
        Check if this node has an edge to the given node.

        :param dest_id: ID of the target node.
        :return: True if edge exists, False otherwise.
        """
        return dest_id in self._neighbors

    @property
    def neighbors(self) -> Iterator[Hashable]:
        """Return an iterator over IDs of neighboring nodes."""
        return iter(self._neighbors)

    @property
    def out_degree(self) -> int:
        """Return the number of outgoing edges."""
        return len(self._neighbors)

    def __repr__(self):
        return f"Node({self.id}, {self._attrs})"


class Graph:
    """Graph data structure supporting directed and undirected graphs."""

    def __init__(self, type: GraphType):
        """
        Initialize a graph with the given type.

        :param type: GraphType.DIRECTED or GraphType.UNDIRECTED
        """
        self.type = type
        self._nodes: Dict[Hashable, Node] = {}

    def add_node(self, node_id: Hashable, attrs: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new node to the graph.

        :param node_id: Unique node identifier.
        :param attrs: Optional dictionary of attributes.
        :raises ValueError: If the node already exists.
        """
        if node_id in self._nodes:
            raise ValueError(f"Node {node_id} already exists")
        self._create_node(node_id, attrs if attrs is not None else {})

    def add_edge(self, src_id: Hashable, dst_id: Hashable, attrs: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new edge to the graph. Nodes are created automatically if missing.

        :param src_id: Source node ID.
        :param dst_id: Destination node ID.
        :param attrs: Optional dictionary of edge attributes.
        :raises ValueError: If the edge already exists.
        """
        if src_id not in self._nodes:
            self._create_node(src_id, {})
        if dst_id not in self._nodes:
            self._create_node(dst_id, {})
        self._set_edge(src_id, dst_id, attrs)
        if self.type == GraphType.UNDIRECTED:
            self._set_edge(dst_id, src_id, attrs)

    def __contains__(self, node_id: Hashable) -> bool:
        """Check whether a node exists in the graph."""
        return node_id in self._nodes

    def __len__(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    def __iter__(self) -> Iterator[Hashable]:
        """Iterate over node IDs in the graph."""
        return iter(self._nodes)

    def node(self, node_id: Hashable) -> Node:
        """
        Get the Node instance with the given ID.

        :param node_id: The ID of the node.
        :return: Node instance.
        :raises KeyError: If the node does not exist.
        """
        return self._nodes[node_id]

    def _create_node(self, node_id: Hashable, attrs: Optional[Dict[str, Any]] = None) -> None:
        """Internal method to create a node."""
        self._nodes[node_id] = Node(node_id, attrs)

    def _set_edge(self, src_id: Hashable, target_id: Hashable, attrs: Dict[str, Any]) -> None:
        """Internal method to create a directed edge."""
        if target_id in self._nodes[src_id]._neighbors:
            raise ValueError(f"Edge {src_id}→{target_id} already exists")
        self._nodes[src_id]._neighbors[target_id] = attrs

    def __repr__(self):
        edges = sum(node.out_degree for node in self._nodes.values())
        if self.type == GraphType.UNDIRECTED:
            edges //= 2
        return f"Graph({self.type}, nodes: {len(self._nodes)}, edges: {edges})"

    def to_dot(self, label_attr:str ="label", weight_attr:str = "weight") -> str:
        """
        Generate a simple Graphviz (DOT) representation of the graph.

        :return: String in DOT language.
        """
        lines = []
        name = "G"
        connector = "->" if self.type == GraphType.DIRECTED else "--"

        lines.append(f'digraph {name} {{' if self.type == GraphType.DIRECTED else f'graph {name} {{')

        # Nodes
        for node_id in self:
            node = self.node(node_id)
            label = node[label_attr] if label_attr in node._attrs else str(node_id)
            lines.append(f'    "{node_id}" [label="{label}"];')

        # Edges
        seen = set()
        for node_id in self:
            node = self.node(node_id)
            for dst_id in node.neighbors:
                if self.type == GraphType.UNDIRECTED and (dst_id, node_id) in seen:
                    continue
                seen.add((node_id, dst_id))
                edge = node.to(dst_id)
                label = edge[weight_attr] if weight_attr in edge._attrs else ""
                lines.append(f'    "{node_id}" {connector} "{dst_id}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)


    def export_to_png(self, filename: str) -> None:
        """
        Export the graph to a PNG file using Graphviz (dot), via pipe.

        :param filename: Output PNG filename.
        :raises RuntimeError: If Graphviz 'dot' command fails.
        """
        dot_data = self.to_dot()
        try:
            subprocess.run(
                ["dot", "-Tpng", "-o", filename],
                input=dot_data,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Graphviz 'dot' command failed: {e}") from e



if __name__ == "__main__":
    # Create a directed graph
    g = Graph(GraphType.DIRECTED)

    # Add nodes with attributes
    g.add_node("A", {"label": "Start", "color": "green"})
    g.add_node("B", {"label": "Middle", "color": "yellow"})
    g.add_node("C", {"label": "End", "color": "red"})
    g.add_node("D", {"label": "Optional", "color": "blue"})

    # Add edges with attributes
    g.add_edge("A", "B", {"weight": 1.0, "type": "normal"})
    g.add_edge("B", "C", {"weight": 2.5, "type": "critical"})
    g.add_edge("A", "D", {"weight": 0.8, "type": "optional"})
    g.add_edge("D", "C", {"weight": 1.7, "type": "fallback"})

    # Access and update node attribute
    print("Node A color:", g.node("A")["color"])
    g.node("A")["color"] = "darkgreen"

    # Access edge and modify its weight
    edge = g.node("A").to("B")
    print("Edge A→B weight:", edge["weight"])
    edge["weight"] = 1.1

    # Iterate through the graph
    print("\nGraph structure:")
    for node_id in g:
        node = g.node(node_id)
        print(f"Node {node.id}: label={node['label']}, out_degree={node.out_degree}")
        for neighbor_id in node.neighbors:
            edge = node.to(neighbor_id)
            print(f"  → {neighbor_id} (weight={edge['weight']}, type={edge['type']})")

    print("-----------------")
    g.export_to_png("out.png")