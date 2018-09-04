from networkx.classes.graph import Graph


class SnapshotGraph(object):
    def __init__(self, **attr):
        self.graphs = {}
        self.graph.update(attr)
        self.snapshots = []

    def generator(self, start, end):
        snaps_traveled = 0
        snaps = 0

        while snaps < len(self.snapshots):
            iters = 0
            # if the snaps traveled plus the current snapshot is less than start
            # just get the length of the compressed snapshot, and keep moving
            # - Reduces time complexity to O(len(snapshots))

            if snaps_traveled + self.snapshots[snaps][1] < start:
                snaps_traveled += self.snapshots[snaps][1]
                snaps += 1
            else:
                while iters < self.snapshots[snaps][1]:
                    if (snaps_traveled < end) and (snaps_traveled >= start):
                        yield self.snapshots[snaps][0]
                    snaps_traveled += 1

                    if snaps_traveled >= end:
                        return
                    iters += 1
                snaps += 1

    def add_snapshot(self, edges):
        # can store snapshots in a list with a tuple for compressing the memory space it takes up
        # eg. [(s1, 10), (s2, 5), (s3, 1), etc and on]
        # then need method for getting them ans uncompressing
        # - would be nice to use generator? saves on memory at least
        g = Graph()
        g.add_weighted_edges_from(edges)

        # compress graph
        if self.snapshots and (g == self.snapshots[len(self.snapshots) - 1][0]):
            self.snapshots[len(self.snapshots) - 1][1] += 1
        else:
            self.snapshots.append((g, 1))

    def subgraph(self, nodes):
        """ Nodes is a list of nodes that should be found in each subgraph"""
        if len(nodes) != len(self.snapshots):
            raise ValueError('node list({}) must be equal in length to number of snapshots({})'.format(len(nodes), len(self.snapshots)))

        subgraph = SnapshotGraph()
        for snapshot, node_list in zip(self.snapshots, nodes):
            subgraph.snapshots.append(snapshot.subgraph(node_list))
        subgraph.graph = self.graph
        return subgraph

    def degree(self, sbunch=None, nbunch=None):
        # returns a list of degrees for each graph snapshot in snapshots
        # use generator to create list of degrees
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return_degrees = []

        for g in graph_list:
            node_list = list(g.nodes)
            for node in node_list:
                if node in nbunch:
                    return_degrees.append(node.degree())

        return return_degrees

    def number_of_nodes(self, sbunch=None):
        # returns a list of the number of nodes in each graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.number_of_nodes() for g in graph_list]

    def order(self, sbunch=None):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.order() for g in graph_list]

    def has_node(self, n):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.has_node(n) for g in graph_list]

    def degree(self, sbunch=None, nbunch=None, weight=None):
        return [g.degree() for g in self.snapshots]

    def is_multigraph(self):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.is_multigraph() for g in graph_list]

    def is_directed(self):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.is_directed() for g in graph_list]

    def to_directed(self):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.to_directed() for g in graph_list]

    def to_undirected(self):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.to_undirected() for g in graph_list]

    def size(self, weight=None):
        # returns a list of the order of the graph in the range
        min_index = min(sbunch)
        max_index = max(sbunch)
        # get all indexes between min and max
        graph_list = list(self.generator(min_index, max_index))
        # only get the indexes wanted
        graph_list = [graph_list[index - min_index] for index in sbunch]

        return [g.size() for g in graph_list]
