""" Base class for dynamic graphs.

"""
import networkx as nx
from dynetworkx.classes.dynamic_edge import DynamicEdge
from dynetworkx.classes.snapshotgraph import SnapshotGraph

class DynamicGraph(object):

    """ To follow existing convention, we'll assign a variable function for
        the creation of nodes and edges.  Currently we'll only allow the 
        default value of dict, but future expansions should allow the use of  
        custom dict-like objecdts
    """
    def __init__(self, **attr):
        """ Initialize a continuous dynamic graph with edges, name, and graph attributes.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.
        """
        # Sorted edge lists
        self.start_edges = []
        self.end_edges   = []

        self.graph = {} # graph attributes
        self.graph.update(attr)

        self.nodes = {} # Nodes in graph
        self.adj   = {} # adjacency dict

    def __str__(self):
        if 'name' in self.graph:
            return self.graph['name']
        return self.__hash__()

    def __contains__(self, n):
        """Return True if n is a node, False otherwise. Use the expression 'n in G'.
        """
        try:
            return n in self.nodes
        except TypeError:
            return False

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.start_edges

    def add_node(self, n, **attr):
        """ Adds node n to the Dynamic Graph
        """
        if n not in self:
            self.nodes[n] = attr
            self.adj[n] = {}
        else:
            self.nodes.update(attr)

    def sort_edges(self):
        self.start_edges.sort(key=lambda x: x.start_time)
        self.end_edges.sort(key=lambda x: x.end_time)

    def add_edge(self, u, v, start_time, end_time, **attrs):
        """ Creates an undirected edge between node u and node v,
            begining at start_time and finishing at end_time

            Parameters
            ----------
            u: node from
            v: node to
            start_time: time the edge first appears 
            end_time: time the edge is no longer present
        """
        dynamic_edge = DynamicEdge(start_time, end_time, **attrs)
        self.add_dynamic_edge(u, v, dynamic_edge)

    def add_dynamic_edge(self, u, v, dynamic_edge):
        if u not in self:
            self.add_node(u)
        if  v not in self:
            self.add_node(v)

        if u not in self.adj[v]:
            edge_list = []
            self.adj[u][v] = edge_list
            self.adj[v][u] = edge_list

        self.adj[u][v].append(dynamic_edge)
        self.adj[v][u].append(dynamic_edge)
        self.start_edges.append(dynamic_edge) 
        self.end_edges.append(dynamic_edge) 

    def add_dynamic_edges_from(self, ebunch):
        """ Adds edges from an iterable ebunch to the DynamicGraph

            Parameters
            ----------
            ebunch: an iterable tuple (u, v, dynamic_edge)

        """
        for u, v, dynamic_edge in ebunch:
            self.add_dynamic_edge(u, v, dynamic_edge)

    def timestamp_filter(self, start_time, end_time):
        """ Creates a static graph of all nodes and edges that exist between
            start_time and end_time
            
            Parameters
            ----------
            start_time: the beginging time of the filter
            end_Time: the end time of the filter

            Returns
            -------
            A dynamic graph with the same graph attributes, and only edges that
            start on or after start_time, and edges that finish before or on
            end_time
        """
        G = DynamicGraph(**self.graph)
        edges = []
        for u in self.adj.keys:
            for v in self.adj[u]:
                for dynamic_edge in self.adj[u][v]:
                    if dynamic_edge.within_snapshot_window(snapshot_start, snapshot_end):
                        edge = (u, v, dynamic_edge)
                        edges.append(edge)
        G.add_dynamic_edges_from(new_edges)
        return G

    def node_filter(self, nbunch):
        """ Creates a dynamic subgraph consisting of only nodges and edges that
            are in nbunch

            Parameters
            ----------
            nbunch: nodes that should be included in the subgraph

            Returns
            -------
            A dynamic graph only populated nodes specified in nbunch
        """
        G = DynamicGraph(self.graph)
        for node in nbunch:
            G.add_node(node, self.nodes[node])
            for neighbor_node in set(nbunch).intersection(self.nodes[node]):
                G.add_node(neighbor_node, self.nodes[neighbor_node])
                dynamic_edge = self.nodes[node][neighbor_node]
                G.add_dynamic_edge(node, neighbor_node,dynamic_edge)
        return G

    def coarsen(self, node_dict):
        """ Returns a dynamic graph where multiple nodes have been combined 
            together into a supernode

            Parameters
            ----------

            node_dict: A mapping of supernodes to list of nodes
                {
                    supernode_0: [1, ..., i],
                    ...
                    supernode_n: [1, ..., j],
                }
        """
        pass
    
    def to_snapshots(self, number_of_snapshots):
        """ Returns number_of_snapshots snapshots

            Parameters
            ----------
            number_of_snapshots: int, the number of snapshots to create

            Return
            -------
            A SnapshotGraph with number_of_snapshots snapshots.  This is created
            by taking the the duration of the graph (last time - first time)
        """

        snapshot_graph = SnapshotGraph(**self.graph)

        start_time     = self.start_edges[0].start_time
        end_time       = self.end_edges[-1].end_time
        total_duration = end_time - start_time
        snapshot_size  = total_duration / number_of_snapshots

        for i in range(number_of_snapshots):
            snapshot_end = i * snapshot_size
            snapshot_start = snapshot_end - snapshot_size
            edges = []
            for u in self.adj.keys:
                for v in self.adj[u]:
                    for dynamic_edge in self.adj[u][v]:
                        if dynamic_edge.within_snapshot_window(snapshot_start, snapshot_end):
                            weight = dynamic_edge.weight_within_snapshot_window(snapshot_start, snapshot_end, snapshot_size)
                            edge = (u, v, weight)
                            edges.append(edge)
            snapshot_graph.add_snapshot(edges)
        return snapshot_graph
