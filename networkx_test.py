import networkx as nx
import pandas as pd

G = nx.read_edgelist("myhraph.txt", create_using=nx.DiGraph)
nodes = sorted(G.nodes())
A = nx.to_numpy_array(G, nodelist=nodes)
df = pd.DataFrame(A, index=nodes, columns=nodes)
print(df)