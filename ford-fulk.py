from collections import defaultdict, deque

class GraphSCC:
    def __init__(self, vertices):
        """
        Initialize directed graph for SCC computation.
        
        Args:
            vertices: Number of vertices in the graph
        """
        self.V = vertices
        self.graph = defaultdict(list)
    
    def add_edge(self, u, v):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def _dfs_fill_order(self, v, visited, stack):
        """
        DFS to fill vertices in stack according to finish time.
        
        Args:
            v: Current vertex
            visited: Set of visited vertices
            stack: Stack to store vertices by finish time
        """
        visited.add(v)
        
        for neighbor in self.graph[v]:
            if neighbor not in visited:
                self._dfs_fill_order(neighbor, visited, stack)
        
        stack.append(v)
    
    def _dfs_collect_scc(self, v, visited, component):
        """
        DFS to collect all vertices in current SCC.
        
        Args:
            v: Current vertex
            visited: Set of visited vertices
            component: List to store vertices in current SCC
        """
        visited.add(v)
        component.append(v)
        
        for neighbor in self.graph[v]:
            if neighbor not in visited:
                self._dfs_collect_scc(neighbor, visited, component)
    
    def get_transpose(self):
        """
        Get transpose (reverse) of the graph.
        
        Returns:
            Transposed graph
        """
        transposed = GraphSCC(self.V)
        
        for u in self.graph:
            for v in self.graph[u]:
                transposed.add_edge(v, u)
        
        return transposed
    
    def kosaraju_scc(self):
        """
        Find all strongly connected components using Kosaraju's algorithm.
        
        Returns:
            List of SCCs, where each SCC is a list of vertices
        """
        stack = []
        visited = set()
        
        # Step 1: Fill vertices in stack according to their finish times
        for v in range(self.V):
            if v not in visited:
                self._dfs_fill_order(v, visited, stack)
        
        # Step 2: Create transpose graph
        transposed = self.get_transpose()
        
        # Step 3: Process vertices in order of decreasing finish time
        visited.clear()
        sccs = []
        
        while stack:
            v = stack.pop()
            if v not in visited:
                component = []
                transposed._dfs_collect_scc(v, visited, component)
                sccs.append(component)
        
        return sccs
    
    def print_graph(self):
        """Print the graph structure."""
        print("Graph structure (vertex -> [neighbors]):")
        for u in sorted(self.graph.keys()):
            print(f"  {u} -> {self.graph[u]}")


class Graph:
    def __init__(self, vertices):
        """
        Initialize graph with given number of vertices.
        
        Args:
            vertices: Number of vertices in the graph
        """
        self.V = vertices
        self.graph = defaultdict(lambda: defaultdict(int))
    
    def add_edge(self, u, v, capacity):
        """
        Add an edge from u to v with given capacity.
        
        Args:
            u: Source vertex
            v: Destination vertex
            capacity: Maximum flow capacity of the edge
        """
        self.graph[u][v] = capacity
    
    def bfs(self, source, sink, parent):
        """
        Perform BFS to find if there's a path from source to sink.
        Also fills parent array to store the path.
        
        Args:
            source: Starting vertex
            sink: Destination vertex
            parent: Dictionary to store the path
            
        Returns:
            True if path exists, False otherwise
        """
        visited = set([source])
        queue = deque([source])
        
        while queue:
            u = queue.popleft()
            
            for v in self.graph[u]:
                # If not visited and has available capacity
                if v not in visited and self.graph[u][v] > 0:
                    visited.add(v)
                    queue.append(v)
                    parent[v] = u
                    
                    if v == sink:
                        return True
        
        return False
    
    def ford_fulkerson(self, source, sink):
        """
        Implement Ford-Fulkerson algorithm to find maximum flow.
        Uses BFS for finding augmenting paths (Edmonds-Karp variant).
        
        Args:
            source: Source vertex
            sink: Sink vertex
            
        Returns:
            Maximum flow value from source to sink
        """
        parent = {}
        max_flow = 0
        
        # Create a copy of the graph for residual graph
        residual_graph = Graph(self.V)
        for u in self.graph:
            for v in self.graph[u]:
                residual_graph.graph[u][v] = self.graph[u][v]
        
        # While there exists an augmenting path from source to sink
        while residual_graph.bfs(source, sink, parent):
            # Find minimum capacity along the path
            path_flow = float('inf')
            s = sink
            
            while s != source:
                path_flow = min(path_flow, residual_graph.graph[parent[s]][s])
                s = parent[s]
            
            # Add path flow to overall flow
            max_flow += path_flow
            
            # Update residual capacities of edges and reverse edges
            v = sink
            while v != source:
                u = parent[v]
                residual_graph.graph[u][v] -= path_flow
                residual_graph.graph[v][u] += path_flow
                v = parent[v]
            
            # Clear parent for next iteration
            parent = {}
        
        return max_flow
    
    def print_graph(self):
        """Print the graph structure."""
        print("Graph structure (vertex -> {neighbor: capacity}):")
        for u in sorted(self.graph.keys()):
            print(f"  {u} -> {dict(self.graph[u])}")


# Example usage
if __name__ == "__main__":
    # Create a graph with 6 vertices (0 to 5)
    g = Graph(6)
    
    # Add edges with capacities
    # Format: add_edge(from, to, capacity)
    g.add_edge(0, 1, 16)
    g.add_edge(0, 2, 13)
    g.add_edge(1, 2, 10)
    g.add_edge(1, 3, 12)
    g.add_edge(2, 1, 4)
    g.add_edge(2, 4, 14)
    g.add_edge(3, 2, 9)
    g.add_edge(3, 5, 20)
    g.add_edge(4, 3, 7)
    g.add_edge(4, 5, 4)
    
    print("Original graph:")
    g.print_graph()
    
    source = 0
    sink = 5
    
    max_flow = g.ford_fulkerson(source, sink)
    
    print(f"\nMaximum flow from vertex {source} to vertex {sink}: {max_flow}")
    
    # Example 2: Simple graph
    print("\n" + "="*50)
    print("Example 2: Simpler graph")
    print("="*50)
    
    g2 = Graph(4)
    g2.add_edge(0, 1, 10)
    g2.add_edge(0, 2, 10)
    g2.add_edge(1, 2, 2)
    g2.add_edge(1, 3, 4)
    g2.add_edge(2, 3, 9)
    
    print("Original graph:")
    g2.print_graph()
    
    max_flow2 = g2.ford_fulkerson(0, 3)
    print(f"\nMaximum flow from vertex 0 to vertex 3: {max_flow2}")
    
    # Strongly Connected Components (SCC) Examples
    print("\n" + "="*50)
    print("Strongly Connected Components (Kosaraju's Algorithm)")
    print("="*50)
    
    # Example 1: Graph with multiple SCCs
    print("\nExample 1: Graph with 5 vertices")
    g_scc = GraphSCC(5)
    g_scc.add_edge(0, 1)
    g_scc.add_edge(1, 2)
    g_scc.add_edge(2, 0)
    g_scc.add_edge(1, 3)
    g_scc.add_edge(3, 4)
    
    print("Original graph:")
    g_scc.print_graph()
    
    sccs = g_scc.kosaraju_scc()
    print(f"\nNumber of SCCs: {len(sccs)}")
    for i, scc in enumerate(sccs, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    
    # Example 2: More complex graph
    print("\nExample 2: Graph with 8 vertices")
    g_scc2 = GraphSCC(8)
    g_scc2.add_edge(0, 1)
    g_scc2.add_edge(1, 2)
    g_scc2.add_edge(2, 3)
    g_scc2.add_edge(2, 4)
    g_scc2.add_edge(3, 0)
    g_scc2.add_edge(4, 5)
    g_scc2.add_edge(5, 6)
    g_scc2.add_edge(6, 4)
    g_scc2.add_edge(6, 7)
    
    print("Original graph:")
    g_scc2.print_graph()
    
    sccs2 = g_scc2.kosaraju_scc()
    print(f"\nNumber of SCCs: {len(sccs2)}")
    for i, scc in enumerate(sccs2, 1):
        print(f"  SCC {i}: {sorted(scc)}")
