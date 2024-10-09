import scott as st
import pandas as pd
from jaal import Jaal
from classes_state_representation import *
import PyBliss as pb
import networkx as nx


class Math:

    def __init__(self):
        self.plus = BinaryOperator("+", "+", None)
        self.minus = BinaryOperator("-", "-", None)
        self.multi = BinaryOperator("*", "*", None)
        self.divid = BinaryOperator("/", "/", None)
        #equal_tzi = BinaryOperator("=", "==", ['t','z','i']) # equation index only applies to =
        self.equal_zi = BinaryOperator("=", "==", ['z','i','n']) # equation index only applies to =
        self.equal_zp = BinaryOperator("=", "==", ['z','p','n']) # equation index only applies to =
        self.equal_p = BinaryOperator("=", "==", ['p','n']) # equation index only applies to =
        self.equal_i = BinaryOperator("=", "==", ['i','n']) # equation index only applies to =
        self.equal_isolo = BinaryOperator("=", "==", ['i']) # equation index only applies to =
        self.equal_i_VPFR = BinaryOperator("=", "==", ['i','V_PFR']) # equation index only applies to =
        self.equal_ip = BinaryOperator("=", "==", ['i','p','n'])
        self.equal = BinaryOperator("=", "==", ['n'])
        self.equal_noind = BinaryOperator("=", "==", None)
        self.equal_t = BinaryOperator("=", "==", ['t'])
        self.equal_texept0 = BinaryOperator("=exept0", "==", ['t'])
        self.power = BinaryOperator("^", "**", None)
        self.geq = BinaryOperator(">=",">=",None)
        self.leq = BinaryOperator("<=","<=",None)

        # Define unary operators (Defining new unary operators requires adding pyomo string to the parser itself.)
        self.expon = UnaryOperator("expon", "exp(", None) # Specify index on which to perform operator, doesnt apply to exp. 
        self.sumop_p = UnaryOperator("sumop_p", "sum(", ['p']) 
        self.sumop_tau = UnaryOperator("sumop_tau", "sum(", ['tau'])
        self.sumop_tau_iftgeqtau = UnaryOperator("sumop_tau_iftgeqtau", "sum(", ['tau'])
        self.sumop_multitau = UnaryOperator("sumop_multitau", "sum(", ['tau']) 
        self.prodop_i = UnaryOperator("prodop_i", "prod(", ['i']) 
        self.shift = UnaryOperator("shift","shift",['tau'])
        self.index0 = UnaryOperator("index0","index0",None)
        self.indexm1 = UnaryOperator("indexm1","indexm1",None)
        self.indexPFR0 = UnaryOperator("indexPFR0","indexPFR0",None)

class TopologyObject:

    def __init__(self, name):
        self.name = name
        self.identifier = None
        self.phenomena = []
        self.color = None
        self.math = Math()
        self.eq_library = {}
        self.exclusive_eqs = []
    
    def assign_phenomenon(self, phenomenon):
        self.phenomena.append(phenomenon)

    def compile_libraries(self):
        for phenomenon in self.phenomena:
            phenomenon.generate_eqlib(self)

class Compartment(TopologyObject):

    def __init__(self, name):
        super().__init__(name)
        self.is_environment = False
        self.is_dummy = False
        self.interfaces_in = []
        self.interfaces_out = []
        self.connections = []
        self.color = 888888888

    def interface_type_qualifier(self):
        new_connection_types_temp = []
        new_connection_types = new_connection_types_temp
        for connection in self.connections:
            # if not connection["optional"]:
                new_connection_types_temp.append(connection)
        for interface in self.interfaces_in:
            for connection in new_connection_types_temp:
                if type(interface) == connection["connection_type"] and connection["direction"] == "in" and interface.connection_to_id == connection["id"]:
                    new_connection_types.remove(connection)
                    break
        for interface in self.interfaces_out:
            for connection in new_connection_types_temp:
                if type(interface) == connection["connection_type"] and connection["direction"] == "out" and interface.connection_from_id == connection["id"]:
                    new_connection_types.remove(connection)
                    break

        return new_connection_types
    
    def get_optional_connections(self):
        optional_connections = []
        for connection in self.connections:
            if connection["optional"]:
                optional_connections.append(connection)
        return optional_connections

class Interface(TopologyObject):

    def __init__(self, name):
        super().__init__(name)
        self.compartment_from = None
        self.compartment_to = None
        self.is_open = True
        self.is_optional = False
        self.symbol = {}
        self.connection_from_id = None
        self.connection_to_id = None
        self.is_envflow_in = False
        self.is_envflow_out = False

class Phenomenon:

    def __init__(self, identifier : str, type : str, can_compartment : bool, can_interface : bool, **kwargs):
        self.identifier = identifier
        self.type = type
        self.can_compartment = can_compartment
        self.can_interface = can_interface
        self.assigned = False
        self.host_object = None
        self.eq_library = {}
        self.known_start = kwargs.get("known_start", None)
        self.known_end = kwargs.get("known_end", None)

        self.math = Math()

        def generate_eqlib(host):
            return True
        self.generate_eqlib = generate_eqlib

class Topology:

    def __init__(self, building_blocks : list):
        self.compartments = []
        self.interfaces = []
        self.building_blocks = building_blocks
        self.libraries = []
        self.completed = False
        self.interface_counter = 1
        self.compartment_counter = 0

    def add_compartment(self, compartment : Compartment):
        self.compartments.append(compartment)
        self.compartment_counter += 1

    def num_compartments(self):
        count = 0
        for compartment in self.compartments:
            if not (compartment.is_dummy or compartment.is_environment):
                count += 1
        return count

    def add_interface(self, interface : Interface):
        self.interfaces.append(interface)
        self.interface_counter += 1

    def has_open_interface(self, optional):
        for interface in self.interfaces:
            if optional:
                if interface.is_open and not interface.is_optional:
                    return True
            else:
                if interface.is_open:
                    return True
        return False
        
    def has_blank_closed_interfaces(self):
        for interface in self.interfaces:
            if not interface.is_open and len(interface.phenomena) == 0:
                return True
        return False
        
    def get_phenomenon_by_type(self, type : str):
        # Get the first phenomenon of a specific type
        _phenomenon = None
        for phenomenon in self.phenomena:
            if phenomenon.type == type:
                _phenomenon = phenomenon
        return _phenomenon

    def get_object(self, identifier : str):
        # Return an interface or compartment with that identifier
        _object = None
        for interface in self.interfaces:
            if interface.identifier == identifier:
                _object = interface
        for compartment in self.compartments:
            if compartment.identifier == identifier:
                _object = compartment
        return _object
    
    def get_object_colors(self):
        # Add connection information to colors to identify at how the compartments are connected
        self.connection_colors = {}
        connection_color_base = 1000000000
        for interface in self.interfaces:
            self.connection_colors[interface] = {}
            self.connection_colors[interface]["connection_from"] = connection_color_base
            self.connection_colors[interface]["connection_to"] = connection_color_base
            if interface.connection_from_id is not None and interface.connection_to_id is not None:
                self.connection_colors[interface]["connection_from"] += interface.connection_from_id
                self.connection_colors[interface]["connection_to"] += interface.connection_to_id

    def get_canon_trace(self):
        # Get canonical string of graph with scott
        graph = st.structs.graph.Graph()
        for compartment in self.compartments:
            graph.add_node(st.structs.node.Node(compartment.identifier, compartment.color))
        
        edgename = 0
        for interface in self.interfaces:
            graph.add_node(st.structs.node.Node(str(interface.identifier) + "_connection_from", self.connection_colors[interface]["connection_from"]))
            graph.add_node(st.structs.node.Node(str(interface.identifier), interface.color))
            graph.add_node(st.structs.node.Node(str(interface.identifier) + "_direction", "D"))
            graph.add_node(st.structs.node.Node(str(interface.identifier) + "_connection_to", self.connection_colors[interface]["connection_to"]))
            graph.add_edge(st.structs.edge.Edge(str(edgename), graph.V[str(interface.compartment_from.identifier)], graph.V[str(interface.identifier) + "_connection_from"]))
            edgename += 1
            graph.add_edge(st.structs.edge.Edge(str(edgename), graph.V[str(interface.identifier) + "_connection_from"], graph.V[str(interface.identifier)]))
            edgename += 1
            graph.add_edge(st.structs.edge.Edge(str(edgename), graph.V[str(interface.identifier)], graph.V[str(interface.identifier) + "_direction"]))
            edgename += 1
            graph.add_edge(st.structs.edge.Edge(str(edgename), graph.V[str(interface.identifier) + "_direction"], graph.V[str(interface.identifier) + "_connection_to"]))
            edgename += 1
            graph.add_edge(st.structs.edge.Edge(str(edgename), graph.V[str(interface.identifier) + "_connection_to"], graph.V[str(interface.compartment_to.identifier)]))
            edgename += 1

        cgraph = st.canonize.to_cgraph(graph)
        self.canonical_form = str(cgraph)

        ### Append labeling to fingerprint because there seems to be some error in scott for the symbol_to / symbol_from nodes
        self.canonical_form += "+" + str(list(self.canonical_labeling_dict.values()))

    def get_canon_labels(self):
        # Relabel a graph with its canonical labels using PyBliss
        graph = pb.Graph()
        for compartment in self.compartments:
            graph.add_vertex(compartment.name, color = compartment.color)
        for interface in self.interfaces:
            graph.add_vertex(interface.name + "_connection_from", color = self.connection_colors[interface]["connection_from"])
            graph.add_vertex(interface.name, color = interface.color)
            graph.add_vertex(interface.name + "_direction", color = 999999999)
            graph.add_vertex(interface.name + "_connection_to", color = self.connection_colors[interface]["connection_to"])
            graph.add_edge(interface.compartment_from.name, interface.name + "_connection_from")
            graph.add_edge(interface.name + "_connection_from", interface.name)
            graph.add_edge(interface.name, interface.name + "_direction")
            graph.add_edge(interface.name + "_direction", interface.name + "_connection_to")
            graph.add_edge(interface.name + "_connection_to", interface.compartment_to.name)
        self.canonical_labeling_dict = graph.canonical_labeling()
        
        # Apply canonical identifiers
        for object in (self.compartments + self.interfaces):
            object.identifier = self.canonical_labeling_dict[object.name]

    def print_to_jaal(self, plot=True):
        edge_data = []
        for interface in self.interfaces:
            edge_data.append({"id":interface.identifier, "from":interface.compartment_from.name, "to":interface.compartment_to.name, "phenomena": ' '.join([phenomenon.identifier for phenomenon in interface.phenomena]), "label": str(interface.name)})

        node_data = []
        for compartment in self.compartments:
            node_data.append({"id":compartment.name, "phenomena": '; '.join([phenomenon.identifier for phenomenon in compartment.phenomena]), "type":type(compartment).__name__})

        edge_df = pd.DataFrame(edge_data)
        node_df = pd.DataFrame(node_data)

        # Jaal error when two edges between a pair of nodes if there are duplicates in the node_df, so combine out duplicates for visualization
        edge_noDups_df = edge_df.groupby(['from', 'to'])['phenomena'].apply(set).apply(", ".join).reset_index()

        if plot:
            Jaal(edge_noDups_df, node_df).plot(directed=True)
        else:
            return edge_noDups_df, node_df

    def find_disconnecting_pairs(self):
        # Subroutine for finding pairs of edges that should not be deleted at the same time, because it would disconnect the graph. NOT USED
        graph = nx.MultiGraph()
        for compartment in self.compartments:
            graph.add_node(compartment.identifier)
        
        for interface in self.interfaces:
            graph.add_edge(interface.compartment_from.identifier,interface.compartment_to.identifier, name=interface.identifier)

        disconnecting_pairs = []
        edges = list(graph.edges(data=True))
        
        # Iterate over all pairs of edges
        for i in range(len(edges)):
            for j in range(i + 1, len(edges)):
                e1, e2 = edges[i], edges[j]
                
                # Create a new graph by removing both edges
                G_prime = graph.copy()
                G_prime.remove_edge(e1[0], e1[1])
                G_prime.remove_edge(e2[0], e2[1])

                # dummys are allowed to be disconnected
                for compartment in self.compartments:
                    if compartment.is_dummy:
                        G_prime.remove_node(compartment.identifier)

                # Check if the graph is still connected
                if not nx.is_connected(G_prime):
                    e1_name = e1[2].get('name', (e1[0], e1[1]))
                    e2_name = e2[2].get('name', (e2[0], e2[1]))
                    disconnecting_pairs.append((e1_name, e2_name))

        self.disconnecting_pairs = disconnecting_pairs
