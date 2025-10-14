class Graph:
    class Vertex:
        __slots__ = '_element'
        def __init__(self, x):
            self._element = x
        def element(self):
            return self._element
        def __hash__(self):
            return hash(id(self))
        def __str__(self):
            return str(self._element)
    class Edge:
        __slots__ = '_origin', '_destination', '_element'
        def __init__(self, origin, destination, element):
            self._origin = origin
            self._destination = destination
            self._element = element
        def endpoints(self):
            return self._origin, self._destination
        def opposite(self, v):
            if not isinstance(v, Graph.Vertex):
                raise TypeError('v mora biti instanca klase Vertex')
            if self._destination == v:
                return self._origin
            elif self._origin == v:
                return self._destination
            raise ValueError('v nije čvor ivice')
        def element(self):
            return self._element
        def __hash__(self):
            return hash((self._origin, self._destination))
        def __str__(self):
            return f'({self._origin},{self._destination},{self._element})'
    def __init__(self, directed=False):
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
    def _validate_vertex(self, v):
        if not isinstance(v, self.Vertex):
            raise TypeError('Očekivan je objekat klase Vertex')
        if v not in self._outgoing:
            raise ValueError('Vertex ne pripada ovom grafu.')
    def is_directed(self):
        return self._incoming is not self._outgoing
    def vertex_count(self):
        return len(self._outgoing)
    def vertices(self):
        return self._outgoing.keys()
    def edge_count(self):
        total = sum(len(self._outgoing[v]) for v in self._outgoing)
        return total if self.is_directed() else total // 2
    def edges(self):
        result = set()
        for secondary_map in self._outgoing.values():
            result.update(secondary_map.values())
        return result
    def get_edge(self, u, v):
        self._validate_vertex(u)
        self._validate_vertex(v)
        return self._outgoing[u].get(v)
    def degree(self, v, outgoing=True):
        self._validate_vertex(v)
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])
    def incident_edges(self, v, outgoing=True):
        self._validate_vertex(v)
        adj = self._outgoing if outgoing else self._incoming
        for edge in adj[v].values():
            yield edge
    def insert_vertex(self, x=None):
        v = self.Vertex(x)
        self._outgoing[v] = {}
        if self.is_directed():
            self._incoming[v] = {}
        return v
    def insert_edge(self, u, v, x=None):
        if self.get_edge(u, v) is not None:
            raise ValueError('u and v are already adjacent')
        e = self.Edge(u, v, x)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e

class PopularityGraph:
    def __init__(self):
        self.graph = Graph(directed=True)
        self.vertex_map = {}
        self.received_count = {}
        self.received_duration = {}
    def _get_or_create_vertex(self, number):
        if number not in self.vertex_map:
            v = self.graph.insert_vertex(number)
            self.vertex_map[number] = v
        return self.vertex_map[number]
    def record_call(self, caller_number, callee_number, duration_time):
        if not caller_number or not callee_number:
            return
        v1 = self._get_or_create_vertex(caller_number)
        v2 = self._get_or_create_vertex(callee_number)
        edge = self.graph.get_edge(v1, v2)
        if edge is None:
            self.graph.insert_edge(v1, v2, {"count": 1, "duration": duration_time})
        else:
            e = edge.element()
            e["count"] += 1
            e["duration"] += duration_time
        self.received_count[callee_number] = self.received_count.get(callee_number, 0) + 1
        self.received_duration[callee_number] = self.received_duration.get(callee_number, 0.0) + duration_time
    #def get_score(self, number): 
    #    c = self.received_count.get(number, 0) 
    #    d = self.received_duration.get(number, 0.0) 
    #    return c * 100 + d 
    #def top_n(self, n=10): 
    #    scores = [(num, self.get_score(num)) for num in self.received_count] 
    #    scores.sort(key=lambda x: x[1], reverse=True) 
    #    return scores[:n]
    def get_score(self, number):
        if number not in self.vertex_map:
            return 0
        v = self.vertex_map[number]
        in_degree = self.graph.degree(v, outgoing=False)
        out_degree = self.graph.degree(v, outgoing=True)
        in_duration = 0.0
        for edge in self.graph.incident_edges(v, outgoing=False):
            in_duration += edge.element()["duration"]
        out_duration = 0.0
        for edge in self.graph.incident_edges(v, outgoing=True):
            out_duration += edge.element()["duration"]
        score = (in_degree * 2 + out_degree) * 100 + (in_duration + 0.5 * out_duration)
        return score
    def top_n(self, n=10):
        scores = [(num, self.get_score(num)) for num in self.vertex_map]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:n]
    def serialize(self):
        data = {"graph": {}, "received_count": self.received_count, "received_duration": self.received_duration}
        for edge in self.graph.edges():
            u, v = edge.endpoints()
            u_num = u.element()
            v_num = v.element()
            e_data = edge.element()
            if u_num not in data["graph"]:
                data["graph"][u_num] = {}
            data["graph"][u_num][v_num] = {"count": e_data["count"], "duration": e_data["duration"]}
        return data
    def deserialize(self, obj):
        self.graph = Graph(directed=True)
        self.vertex_map.clear()
        self.received_count = obj.get("received_count", {})
        self.received_duration = obj.get("received_duration", {})
        for caller, callees in obj.get("graph", {}).items():
            v1 = self._get_or_create_vertex(caller)
            for callee, info in callees.items():
                v2 = self._get_or_create_vertex(callee)
                self.graph.insert_edge(v1, v2, {"count": int(info["count"]), "duration": float(info["duration"])})
    def show_all(self):
        for edge in self.graph.edges():
            u, v = edge.endpoints()
            d = edge.element()
            print(f"{u.element()} -> {v.element()} | count={d['count']}, duration={d['duration']}")
    def clear(self):
        self.graph = Graph(directed=True)
        self.vertex_map.clear()
        self.received_count.clear()
        self.received_duration.clear()
