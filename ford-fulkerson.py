"""
Ford-Fulkerson Algorithm for Maximum Flow

This module implements the Ford-Fulkerson method for computing the maximum
flow in a flow network. It uses BFS to find augmenting paths (Edmonds-Karp).
"""

from collections import deque
from typing import Dict, List, Optional, Tuple


class FlowNetwork:
    """Represents a flow network with capacities and flow tracking."""

    def __init__(self, num_vertices: int):
        """Initialize a flow network with the given number of vertices."""
        self.num_vertices = num_vertices
        self.graph: Dict[int, Dict[int, int]] = {i: {} for i in range(num_vertices)}
        self.flow: Dict[int, Dict[int, int]] = {i: {} for i in range(num_vertices)}

    def add_edge(self, u: int, v: int, capacity: int) -> None:
        """Add an edge from u to v with the given capacity."""
        if v not in self.graph[u]:
            self.graph[u][v] = 0
            self.graph[v][u] = 0
            self.flow[u][v] = 0
            self.flow[v][u] = 0
        self.graph[u][v] += capacity

    def get_residual_capacity(self, u: int, v: int) -> int:
        """Get the residual capacity of edge (u, v)."""
        return self.graph[u].get(v, 0) - self.flow[u].get(v, 0)

    def update_flow(self, u: int, v: int, amount: int) -> None:
        """Update flow along edge (u, v) by the given amount."""
        self.flow[u][v] = self.flow[u].get(v, 0) + amount
        self.flow[v][u] = self.flow[v].get(u, 0) - amount


def bfs_find_path(
    network: FlowNetwork,
    source: int,
    sink: int
) -> Optional[List[int]]:
    """
    Use BFS to find an augmenting path from source to sink.

    Returns the path as a list of vertices, or None if no path exists.
    """
    visited = {source}
    parent: Dict[int, int] = {}
    queue = deque([source])

    while queue:
        current = queue.popleft()

        if current == sink:
            path = []
            node = sink
            while node != source:
                path.append(node)
                node = parent[node]
            path.append(source)
            return path[::-1]

        for neighbor in network.graph[current]:
            if neighbor not in visited:
                residual = network.get_residual_capacity(current, neighbor)
                if residual > 0:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

    return None


def ford_fulkerson(network: FlowNetwork, source: int, sink: int) -> int:
    """
    Compute the maximum flow from source to sink using Ford-Fulkerson.

    This implementation uses BFS to find augmenting paths (Edmonds-Karp variant).
    Time complexity: O(VE^2)
    """
    max_flow = 0

    while True:
        path = bfs_find_path(network, source, sink)
        if path is None:
            break

        # Find minimum residual capacity along the path
        path_flow = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual = network.get_residual_capacity(u, v)
            path_flow = min(path_flow, residual)

        # Update flow along the path
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            network.update_flow(u, v, path_flow)

        max_flow += path_flow

    return max_flow


def find_min_cut(
    network: FlowNetwork,
    source: int
) -> Tuple[set, set]:
    """
    Find the minimum cut after max flow has been computed.

    Returns two sets: vertices reachable from source, and the rest.
    """
    reachable = {source}
    queue = deque([source])

    while queue:
        current = queue.popleft()
        for neighbor in network.graph[current]:
            if neighbor not in reachable:
                if network.get_residual_capacity(current, neighbor) > 0:
                    reachable.add(neighbor)
                    queue.append(neighbor)

    non_reachable = set(range(network.num_vertices)) - reachable
    return reachable, non_reachable


if __name__ == '__main__':
    # Example usage: Classic max flow problem
    n = FlowNetwork(6)

    # Add edges (source=0, sink=5)
    n.add_edge(0, 1, 16)
    n.add_edge(0, 2, 13)
    n.add_edge(1, 2, 10)
    n.add_edge(1, 3, 12)
    n.add_edge(2, 1, 4)
    n.add_edge(2, 4, 14)
    n.add_edge(3, 2, 9)
    n.add_edge(3, 5, 20)
    n.add_edge(4, 3, 7)
    n.add_edge(4, 5, 4)

    max_flow = ford_fulkerson(n, source=0, sink=5)
    print(f"Maximum flow: {max_flow}")

    s_cut, t_cut = find_min_cut(n, source=0)
    print(f"Min-cut S side: {s_cut}")
    print(f"Min-cut T side: {t_cut}")
