from collections import defaultdict, deque

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
