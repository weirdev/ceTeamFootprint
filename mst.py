class mst(object):
    MICUHOME = 17454

    def __init__(self, singleverttomanyfunc, alledgesfunct):
        self.singleverttomanyfunc = singleverttomanyfunc
        self.alledgesfunct = alledgesfunct
        self.edges = set() # { edge }
        self.verticies = dict() # { v : count, ... }
        self.verticies[mst.MICUHOME] = 1 # Home base in MICU (TODO: this actually is just a random room in the micu)
    
    def addvert(self, vertid):
        try:
            self.verticies[vertid] += 1
        except KeyError:
            # We dont already have this vertex so add to to the vertex list
            self.verticies[vertid] = 1
            # Create a node for each vert, so each edge referrs to a common set of nodes
            nodeverticies = dict()
            for simplev in self.verticies:
                nodeverticies[simplev] = DisjointSetNode(simplev)
            # Now add all edges connecting the new vertex to the existing MST
            newedges = self.singleverttomanyfunc(vertid, self.verticies.keys())
            graphedges = set()
            for edge in self.edges:
                nodeverts = []
                for v in edge._verts:
                    nodeverts.append(nodeverticies[v])
                edge._verts = set(nodeverts)
                graphedges.add(edge)
            for edge in newedges:
                graphedges.add(GraphEdge(nodeverticies[vertid], nodeverticies[edge["dst"]], edge["cost"]))

            self.edges = self.spantreefromgraph(graphedges)

    def removevert(self, vertid):
        removedvert = vertid
        self.verticies[removedvert] -= 1
        # Only need to update edges if all verts with this id are removed
        if self.verticies[removedvert] == 0:
            del self.verticies[removedvert]
            # Create a node for each vert, so each edge referrs to a common set of nodes
            nodeverticies = dict()
            for simplev in self.verticies:
                nodeverticies[simplev] = DisjointSetNode(simplev)
            response = self.alledgesfunct(self.verticies)
            graphedges = set()
            for edge in response:
                graphedges.add(GraphEdge(nodeverticies[edge["src"]], nodeverticies[edge["dst"]], edge["cost"]))
            self.edges = self.spantreefromgraph(graphedges)

    def spantreefromgraph(self, graphedges):
        mstedges = set() # new set for selected MST edges

        graphedgelist = list(graphedges)
        graphedgelist.sort()

        # Kruskal's algorithm
        for edge in graphedgelist:
            verts = list(edge._verts)
            if verts[0].DS_find() != verts[1].DS_find():
                newedge = GraphEdge(verts[0].vertex, verts[1].vertex, edge.weight)
                mstedges.add(newedge)
                verts[0].DS_union(verts[1])
        return mstedges

    def getweight(self):
        return sum([e.weight for e in self.edges])

    def getall_edgeweights(self):
        return [e.weight for e in self.edges]

    def create_cluster_forest(self):
        # First test with only making one cut = 2 trees in forest
        forest = []
        
        # Handle only one unique vertex
        if len(self.edges) == 0:
            return [list(self.verticies.keys())[0]]
        edgepool = self.edges.copy()
        cutedge = max(edgepool)
        edgepool.remove(cutedge)
        ### Walk graph from each vertex of cutedge

        # vertpool = all remaining verticies
        # if (later) we cut multiple edges, and two cut
        # edges share a vertex, (+other cases) we want to avoid adding the
        # common vertex as two seperate trees
        vertpool = self.verticies.copy()
        startverts = cutedge.getboth()
        for vertex in startverts:
            if vertex not in vertpool:
                continue
            walkqueue = set()
            walkqueue.add(vertex)
            newedges = set()
            while len(walkqueue) != 0:
                searchvert = walkqueue.pop()
                verynewedges = set()
                for edge in edgepool:
                    if searchvert in edge:
                        newedges.add(edge)
                        verynewedges.add(edge)
                        walkqueue.add(edge.getother(searchvert))
                for edge in verynewedges:
                    edgepool.remove(edge)
            if len(newedges) == 0:
                # This only occurs when two cut edges are adjacent
                forest.append(vertex)
            else:
                forest.append(newedges)
        return forest

    def compute_distality(self):
        forest = self.create_cluster_forest()
        micupathlengths = self.micu_pathlengths()
        totalverts = len(self.verticies)
        distality = dict() # { vertex : distality,... }
        for tree in forest:
            allverts = set()
            if isinstance(tree, int):
                allverts.add(tree)
            else:
                for edge in tree:
                    allverts.update(set(edge.getboth()))
            vertcount = len(allverts)
            for vert in allverts:
                distality[vert] = micupathlengths[vert] * totalverts / vertcount
        del distality[mst.MICUHOME]
        return distality

    def micu_pathlengths(self):
        pathlengths = dict()
        walkqueue = { mst.MICUHOME : 0 }
        while len(walkqueue) != 0:
            vertex, distance = walkqueue.popitem()
            pathlengths[vertex] = distance
            for edge in self.edges:
                if vertex in edge:
                    if edge.getother(vertex) in pathlengths:
                        pathlengths[edge.getother(vertex)] = min(pathlengths[edge.getother(vertex)], edge.weight + distance)
                    else:
                        if edge.getother(vertex) in walkqueue:
                            walkqueue[edge.getother(vertex)] = min(walkqueue[edge.getother(vertex)], edge.weight + distance)
                        else:
                            walkqueue[edge.getother(vertex)] = edge.weight + distance
        return pathlengths


class DisjointSetNode(object):
    def __init__(self, vertex):
        self.vertex = vertex
        self.parent = self
        self.rank = 0

    def DS_find(self):
        if self.parent != self:
            self.parent = self.parent.DS_find()
        return self.parent

    def DS_union(self, other):
        root = self.DS_find()
        otherroot = other.DS_find()

        if root == otherroot:
            return

        if root.rank < otherroot.rank:
            root.parent = otherroot
        elif root.rank > otherroot.rank:
            otherroot.parent = root
        else:
            otherroot.parent = root
            root.rank += 1

    def __repr__(self):
        return str(self.vertex)

    def __hash__(self):
        return self.vertex.__hash__()

class GraphEdge(object):
    def __init__(self, v1, v2, weight):
        self._verts = set((v1,v2))
        self.weight = weight

    def hasvertex(self, vertex):
        return vertex in self._verts

    def getone(self):
        for v in self._verts:
            return v

    def getother(self, vertex):
        for v in self._verts:
            if v != vertex:
                return v
        raise ValueError("vertex was not in edge")

    def getboth(self):
        return [v for v in self._verts]

    def __lt__(self, other):
        return self.weight < other.weight
    
    def __le__(self, other):
        return not self.weight > other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __ge__(self, other):
        return not self.weight < other.weight

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, item):
        return item in self._verts
    
    def __hash__(self):
        return tuple(sorted(self._verts)).__hash__()

    def __repr__(self):
        verts = list(self._verts)
        return "{(" + str(verts[0]) + "--" + str(verts[1]) + ") : " + str(self.weight) + '}'
    
        