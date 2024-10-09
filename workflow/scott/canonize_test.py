import scott as st

# Get canonical string of graph with scott
graph = st.structs.graph.Graph()
graph.add_node(st.structs.node.Node("1", "green"))
graph.add_node(st.structs.node.Node("2", "yellow"))
graph.add_node(st.structs.node.Node("3", "blue"))
graph.add_node(st.structs.node.Node("4", "yellow"))


graph.add_edge(st.structs.edge.Edge("e1", graph.V["1"], graph.V["2"], modality="lightblue"))
graph.add_edge(st.structs.edge.Edge("e2", graph.V["1"], graph.V["3"], modality="lightblue"))
graph.add_edge(st.structs.edge.Edge("e3", graph.V["2"], graph.V["4"], modality="red"))
graph.add_edge(st.structs.edge.Edge("e4", graph.V["3"], graph.V["4"], modality="red"))
graph.add_edge(st.structs.edge.Edge("e5", graph.V["4"], graph.V["1"], modality="lightblue"))

cgraph = st.canonize.to_cgraph(graph)
fingerprint = str(cgraph)
print(fingerprint)