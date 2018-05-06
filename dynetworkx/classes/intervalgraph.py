from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
from intervaltree import Interval, IntervalTree
from networkx.classes.multigraph import MultiGraph


class IntervalGraph(object):
    def __init__(self, **attr):
        """Initialize an interval graph with edges, name, or graph attributes.

        Parameters
        ----------
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G = nx.Graph(name='my graph')
        >>> e = [(1, 2), (2, 3), (3, 4)]  # list of edges
        >>> G = nx.Graph(e)

        Arbitrary graph attribute pairs (key=value) may be assigned

        >>> G = nx.Graph(e, day="Friday")
        >>> G.graph
        {'day': 'Friday'}

        """
        self.tree = IntervalTree()
        self.graph = {}  # dictionary for graph attributes
        self._adj = {}
        self._node = {}

        self.graph.update(attr)

    @property
    def name(self):
        """String identifier of the interval graph.

        This interval graph attribute appears in the attribute dict IG.graph
        keyed by the string `"name"`. as well as an attribute (technically
        a property) `IG.name`. This is entirely user controlled.
        """
        return self.graph.get('name', '')

    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __str__(self):
        """Return the interval graph name.

        Returns
        -------
        name : string
            The name of the interval graph.

        Examples
        --------
        >>> IG = dnx.Graph(name='foo')
        >>> str(G)
        'foo'
        """
        return self.name

    def __len__(self):
        """Return the number of nodes. Use: 'len(G)'.

        Returns
        -------
        nnodes : int
            The number of nodes in the graph.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> len(G)
        4

        """
        return len(self._node)

    def __contains__(self, n):
        """Return True if n is a node, False otherwise. Use: 'n in G'.

        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> 1 in G
        True
        """
        try:
            return n in self._node
        except TypeError:
            return False

    def interval(self):
        return self.tree.begin(), self.tree.end()

    def add_node(self, node_for_adding, **attr):
        """Add a single node `node_for_adding` and update node attributes.

        Parameters
        ----------
        node_for_adding : node
            A node can be any hashable Python object except None.
        attr : keyword arguments, optional
            Set or change node attributes using key=value.

        See Also
        --------
        add_nodes_from

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3 = nx.Graph([(0, 1), (1, 2), (2, 0)])
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        Use keywords set/change node attributes:

        >>> G.add_node(1, size=10)
        >>> G.add_node(3, weight=0.4, UTM=('13S', 382871, 3972649))

        Notes
        -----
        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.

        On many platforms hashable items also include mutables such as
        NetworkX Graphs, though one should be careful that the hash
        doesn't change on mutables.
        """
        if node_for_adding not in self._node:
            self._adj[node_for_adding] = {}
            self._node[node_for_adding] = attr
        else:  # update attr even if node already exists
            self._node[node_for_adding].update(attr)

    def add_nodes_from(self, nodes_for_adding, **attr):
        """Add multiple nodes.

        Parameters
        ----------
        nodes_for_adding : iterable container
            A container of nodes (list, dict, set, etc.).
            OR
            A container of (node, attribute dict) tuples.
            Node attributes are updated using the attribute dict.
        attr : keyword arguments, optional (default= no attributes)
            Update attributes for all nodes in nodes.
            Node attributes specified in nodes as a tuple take
            precedence over attributes specified via keyword arguments.

        See Also
        --------
        add_node

        Examples
        --------
        >>> G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_nodes_from('Hello')
        >>> K3 = nx.Graph([(0, 1), (1, 2), (2, 0)])
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes(), key=str)
        [0, 1, 2, 'H', 'e', 'l', 'o']

        Use keywords to update specific node attributes for every node.

        >>> G.add_nodes_from([1, 2], size=10)
        >>> G.add_nodes_from([3, 4], weight=0.4)

        Use (node, attrdict) tuples to update attributes for specific nodes.

        >>> G.add_nodes_from([(1, dict(size=11)), (2, {'color':'blue'})])
        >>> G.nodes[1]['size']
        11
        >>> H = nx.Graph()
        >>> H.add_nodes_from(G.nodes(data=True))
        >>> H.nodes[1]['size']
        11

        """
        for n in nodes_for_adding:
            # keep all this inside try/except because
            # CPython throws TypeError on n not in self._node,
            # while pre-2.7.5 ironpython throws on self._adj[n]
            try:
                if n not in self._node:
                    self._adj[n] = {}
                    self._node[n] = attr.copy()
                else:
                    self._node[n].update(attr)
            except TypeError:
                nn, ndict = n
                if nn not in self._node:
                    self._adj[nn] = {}
                    self._node[nn] = attr.copy()
                    self._node[nn].update(ndict)
                else:
                    self._node[nn].update(attr)
                    self._node[nn].update(ndict)

    def number_of_nodes(self, begin=None, end=None):
        """Return the number of nodes in the interval graph between the given interval.

        Parameters
        ----------
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Returns
        -------
        nnodes : int
            The number of nodes in the interval graph.

        See Also
        --------
        __len__

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> len(G)
        3
        """

        if begin is None and end is None:
            return len(self._node)

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        iedges = self.tree[begin:end]

        inodes = set()

        for iv in iedges:
            inodes.add(iv.data[0])
            inodes.add(iv.data[1])

        return len(inodes)

    def has_node(self, n, begin=None, end=None):
        """Return True if the interval graph contains the node n, during the given interval.

        Identical to `n in G` when 'begin' and 'end' are not defined.

        Parameters
        ----------
        n : node
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_node(0)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        """
        try:
            exists_node = n in self._node
        except TypeError:
            exists_node = False

        if (begin is None and end is None) or not exists_node:
            return exists_node

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        iedges = self._adj[n].keys()

        for iv in iedges:
            if iv.overlaps(begin=begin, end=end):
                return True

        return False

    def remove_node(self, n, begin=None, end=None):
        """Remove node n within the given interval.

        Removes the node n and all adjacent edges within the given interval.
        Attempting to remove a non-existent node will raise an exception.

        Parameters
        ----------
        n : node
           A node in the graph
        begin: integer, optional  (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end: integer, optional  (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.

        Raises
        -------
        NetworkXError
           If n is not in the interval graph.

        See Also
        --------
        remove_nodes_from

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> list(G.edges)
        [(0, 1), (1, 2)]
        >>> G.remove_node(1)
        >>> list(G.edges)
        []

        """
        adj = self._adj
        try:
            nbrs = list(adj[n])  # list handles self-loops (allows mutation)
            del self._node[n]
        except KeyError:  # NetworkXError if n not in self
            raise NetworkXError("The node %s is not in the graph." % (n,))
        for u in nbrs:
            del adj[u][n]  # remove all edges n-u in graph
        del adj[n]  # now remove node

    def add_edge(self, u, v, begin, end, **attr):
        """Add an edge between u and v, during interval [begin, end).

        The nodes u and v will be automatically added if they are
        not already in the interval graph.

        Edge attributes can be specified with keywords or by directly
        accessing the edge's attribute dictionary. See examples below.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin: orderable type
            Inclusive beginning time of the edge appearing in the interval graph.
        end: orderable type
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes
        -----
        Adding an edge that already exists updates the edge data.

        Both begin and end must be the same type across all edges in the interval graph. Also, to create
        snapshots, both must be integers.

        Many NetworkX algorithms designed for weighted graphs use
        an edge attribute (by default `weight`) to hold a numerical value.

        Examples
        --------
        The following all add the edge e=(1, 2) to graph G:

        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = (1, 2)
        >>> G.add_edge(1, 2)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from([(1, 2)])  # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)

        For non-string attribute keys, use subscript notation.

        >>> G.add_edge(1, 2)
        >>> G[1][2].update({0: 5})
        >>> G.edges[1, 2].update({0: 5})
        """

        iedge = self.__get_iedge_in_tree(begin, end, u, v)

        # if edge exists, just update attr
        if iedge is not None:
            # since both point to the same attr, updating one is enough
            self._adj[u][iedge].update(attr)
            return

        iedge = Interval(begin, end, (u, v))

        # add nodes
        if u not in self._node:
            self._adj[u] = {}
            self._node[u] = {}
        if v not in self._node:
            self._adj[v] = {}
            self._node[v] = {}

        # add edge
        try:
            self.tree.add(iedge)
        except ValueError:
            raise NetworkXError("IntervalGraph: edge duration must be strictly bigger than zero {0}.".format(iedge))

        self._adj[u][iedge] = self._adj[v][iedge] = attr

    def add_edges_from(self, ebunch_to_add, **attr):
        """Add all the edges in ebunch_to_add.

        Parameters
        ----------
        ebunch_to_add : container of edges
            Each edge given in the container will be added to the
            interval graph. The edges must be given as as 4-tuples (u, v, being, end).
            Both begin and end must be orderable and the same type across all edges.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.

        See Also
        --------
        add_edge : add a single edge

        Notes
        -----
        Adding the same edge (with the same interval) twice has no effect
        but any edge data will be updated when each duplicate edge is added.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0, 1), (1, 2)]) # using a list of edge tuples
        >>> e = zip(range(0, 3), range(1, 4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1, 2), (2, 3)], weight=3)
        >>> G.add_edges_from([(3, 4), (1, 4)], label='WN2898')
        """

        for e in ebunch_to_add:
            if len(e) != 4:
                raise NetworkXError("Edge tuple {0} must be a 4-tuple.".format(e))

            self.add_edge(e[0], e[1], e[2], e[3], **attr)

    def has_edge(self, u, v, begin=None, end=None, overlapping=True):
        """Return True if there exists an edge between u and v
        in the interval graph, during the given interval.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : integer, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the node appearing in the interval graph.
        end : integer, optional (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the node appearing in the interval graph.
            Must be bigger than begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
        overlapping : bool, optional (default= True)
            if True, it returns True if there exists an edge between u and v with
            overlapping interval with `begin` and `end`.
            if False, it returns true only if there exists an edge between u and v
            with the exact interval.
            Note: if False, both `begin` and `end` must be defined, otherwise
            an exception is raised.

        Raises
        ------
        NetworkXError
            If `begin` and `end` are not defined and `overlapping= False`

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_node(0)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        """

        if begin is None and end is None:
            for iv in self._adj[u].keys():
                if iv.data[0] == v or iv.data[1] == v:
                    return True
            return False

        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            return self.__get_iedge_in_tree(u, v, begin, end) is not None

        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        for iv in self._adj[u].keys():
            if (iv.data[0] == v or iv.data[1] == v) and iv.overlaps(begin=begin, end=end):
                return True
        return False

    def remove_edge(self, u, v, begin=None, end=None, overlapping=True):
        """Remove the edge between u and v in the interval graph,
        during the given interval.

        Quiet if the specified edge is not present.

        Parameters
        ----------
        u, v : nodes
            Nodes can be, for example, strings or numbers.
            Nodes must be hashable (and not None) Python objects.
        begin : integer, optional (default= beginning of the entire interval graph)
            Inclusive beginning time of the edge appearing in the interval graph.
        end : integer, optional (default= end of the entire interval graph + 1)
            Non-inclusive ending time of the edge appearing in the interval graph.
            Must be bigger than begin.
            Note that the default value is shifted up by 1 to make it an inclusive end.
        overlapping : bool, optional (default= True)
            if True, remove the edge between u and v with overlapping interval
            with `begin` and `end`.
            if False, remove the edge between u and v with the exact interval.
            Note: if False, both `begin` and `end` must be defined, otherwise
            an exception is raised.

        Raises
        ------
        NetworkXError
            If `begin` and `end` are not defined and `overlapping= False`

        Examples
        --------
        >>> G = nx.path_graph(3)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.has_node(0)
        True

        It is more readable and simpler to use

        >>> 0 in G
        True

        """
        # remove every edge between u and v
        if begin is None and end is None:
            for iv in self._adj[u].keys():
                if iv.data[0] == v or iv.data[1] == v:
                    self.__remove_iedge(iv)
            return

        # remove edge between u and v with the exact given interval
        if not overlapping:
            if begin is None or end is None:
                raise NetworkXError("For exact interval match (overlapping=False), both begin and end must be defined.")

            iedge = self.__get_iedge_in_tree(u, v, begin, end)
            if iedge is None:
                return
            self.__remove_iedge(iedge)
            return

        # remove edge between u and v with overlapping interval with the given interval
        if begin is None:
            begin = self.tree.begin()

        if end is None:
            end = self.tree.end() + 1

        for iv in self._adj[u].keys():
            if (iv.data[0] == v or iv.data[1] == v) and iv.overlaps(begin=begin, end=end):
                self.__remove_iedge(iv)

    def to_subgraph(self, begin, end, multigraph=False, edge_data=False, edge_interval_data=False, node_data=False):
        """Return a networkx Graph or MultiGraph which includes all the nodes and
        edges which have overlapping intervals with the given interval.

        Parameters
        ----------
        begin: orderable type
            Inclusive beginning time of the edge appearing in the interval graph.
            Must be bigger than begin.
        end: orderable type
            Non-inclusive ending time of the edge appearing in the interval graph.
        multigraph: bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_interval_data: bool, optional (default= False)
            If True, each edge's attribute will also include its begin and end interval data.
            If `edge_data= True` and there already exist edge attributes with names begin and end,
            they will be overwritten.
        node_data : bool, optional (default= False)
            if True, each node's attributes will be included.

        See Also
        --------
        to_snapshots : divide the interval graph to snapshots

        Notes
        -----
        If multigraph= False, and edge_data=True or edge_interval_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0, 1), (1, 2)]) # using a list of edge tuples
        >>> e = zip(range(0, 3), range(1, 4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1, 2), (2, 3)], weight=3)
        >>> G.add_edges_from([(3, 4), (1, 4)], label='WN2898')
        """

        # nodes with no edges will be discarded
        # getting all edges within interval

        if end <= begin:
            raise NetworkXError("IntervalGraph: subgraph duration must be strictly bigger than zero: "
                                "begin: {}, end: {}.".format(begin, end))

        iedges = self.tree[begin:end]

        if multigraph:
            G = MultiGraph()
        else:
            G = Graph()

        if edge_data and edge_interval_data:
            G.add_edges_from((iedge.data[0], iedge.data[1],
                              dict(self._adj[iedge.data[0]][iedge], begin=iedge.begin, end=iedge.end))
                             for iedge in iedges)
        elif edge_data:
            G.add_edges_from((iedge.data[0], iedge.data[1], self._adj[iedge.data[0]][iedge].copy())
                             for iedge in iedges)
        elif edge_interval_data:
            G.add_edges_from((iedge.data[0], iedge.data[1], {'begin': iedge.begin, 'end': iedge.end})
                             for iedge in iedges)
        else:
            G.add_edges_from((iedge.data[0], iedge.data[1]) for iedge in iedges)

        # include node attributes
        if node_data:
            G.add_nodes_from((n, self._node[n].copy()) for n in G.nodes)

        return G

    def to_snapshots(self, number_of_snapshots, multigraph=False, edge_data=False, edge_interval_data=False,
                     node_data=False, return_length=False):
        """Return a list of networkx Graph or MultiGraph objects as snapshots
        of the interval graph in consecutive order.

        Parameters
        ----------
        number_of_snapshots : integer
            Number of snapshots to divide the interval graph into.
            Must be bigger than 1.
        multigraph : bool, optional (default= False)
            If True, a networkx MultiGraph will be returned. If False, networkx Graph.
        edge_data: bool, optional (default= False)
            If True, edges will keep their attributes.
        edge_interval_data : bool, optional (default= False)
            If True, each edge's attribute will also include its begin and end interval data.
            If `edge_data= True` and there already exist edge attributes with names begin and end,
            they will be overwritten.
        node_data : bool, optional (default= False)
            if True, each node's attributes will be included.
        return_length : bool, optional (default= False)
            If true, the length of snapshots will be returned as the second argument.

        See Also
        --------
        to_subgraph : subgraph based on an interval

        Notes
        -----
        In order to create snapshots, begin and end interval objects of the interval graph must be numbers.

        If multigraph= False, and edge_data=True or edge_interval_data=True,
        in case there are multiple edges, only one will show with one of the edge's attributes.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0, 1), (1, 2)]) # using a list of edge tuples
        >>> e = zip(range(0, 3), range(1, 4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3

        Associate data to edges

        >>> G.add_edges_from([(1, 2), (2, 3)], weight=3)
        >>> G.add_edges_from([(3, 4), (1, 4)], label='WN2898')
        """

        if number_of_snapshots < 2 or type(number_of_snapshots) is not int:
            raise NetworkXError("IntervalGraph: number of snapshots must be an integer and 2 or bigger. "
                                "{0} was passed.".format(number_of_snapshots))

        begin, end = self.interval()
        snapshot_len = (end - begin) / number_of_snapshots

        snapshots = []
        end_inclusive_addition = 0
        for i in range(number_of_snapshots):
            # since to_subgraph is end non-inclusive, shift the end up by 1 to include end in the last snapshot.
            if i == number_of_snapshots - 1:
                end_inclusive_addition = 1

            snapshots.append(
                self.to_subgraph(begin + snapshot_len * i, begin + snapshot_len * (i + 1) + end_inclusive_addition,
                                 multigraph=multigraph, edge_data=edge_data, edge_interval_data=edge_interval_data,
                                 node_data=node_data))
        if return_length:
            return snapshots, snapshot_len

        return snapshots

    @staticmethod
    def load_from_txt(path, delimiter=" ", nodetype=None, comments="#"):
        """Read interval graph in from path.
           Every line in the file must be an edge in the following format: "node, node, begin, end".
           Both times must be integers.
        Parameters
        ----------
        path : string or file
           Filename to read.

        nodetype : Python type, optional
           Convert nodes to this type.

        comments : string, optional
           Marker for comment lines

        delimiter : string, optional
           Separator for node labels.  The default is whitespace.

        Returns
        -------
        IG: DyNetworkX IntervalGraph
            The graph corresponding to the lines in edge list.

        Examples
        --------
        >>> G=nx.path_graph(4)
        >>> nx.write_adjlist(G, "test.adjlist")
        >>> G=nx.read_adjlist("test.adjlist")

        The path can be a filehandle or a string with the name of the file. If a
        filehandle is provided, it has to be opened in 'rb' mode.

        >>> fh=open("test.adjlist", 'rb')
        >>> G=nx.read_adjlist(fh)

        Filenames ending in .gz or .bz2 will be compressed.

        >>> nx.write_adjlist(G,"test.adjlist.gz")
        >>> G=nx.read_adjlist("test.adjlist.gz")

        The optional nodetype is a function to convert node strings to nodetype.

        For example

        >>> G=nx.read_adjlist("test.adjlist", nodetype=int)

        will attempt to convert all nodes to integer type.

        Since nodes must be hashable, the function nodetype must return hashable
        types (e.g. int, float, str, frozenset - or tuples of those, etc.)

        Notes
        -----
        This format does not store graph or node data.
        Both times must be integers.
        """

        ig = IntervalGraph()

        with open(path, 'r') as file:
            for line in file:
                p = line.find(comments)
                if p >= 0:
                    line = line[:p]
                if not len(line):
                    continue

                line = line.rstrip().split(delimiter)
                u, v, begin, end = line

                if nodetype is not None:
                    try:
                        u = nodetype(u)
                        v = nodetype(v)
                    except:
                        raise TypeError("Failed to convert node to type {0}".format(nodetype))

                try:
                    begin = int(begin)
                    end = nodetype(end)
                except:
                    raise TypeError("Failed to convert time to type int")

                ig.add_edge(u, v, begin, end)

        return ig

    def __remove_iedge(self, iedge):
        self.tree.discard(iedge)
        self._adj[iedge.data[0]].pop(iedge, None)
        self._adj[iedge.data[1]].pop(iedge, None)

    def __get_iedge_in_tree(self, u, v, begin, end):
        temp_iedge = Interval(begin, end, (u, v))
        if temp_iedge in self.tree:
            return temp_iedge

        temp_iedge = Interval(begin, end, (v, u))
        if temp_iedge in self.tree:
            return temp_iedge

        return None
