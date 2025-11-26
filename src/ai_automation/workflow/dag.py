"""Directed Acyclic Graph (DAG) for workflow management."""

import logging
from typing import List, Dict, Set, Optional, Any
from ai_automation.exceptions import WorkflowValidationError

logger = logging.getLogger(__name__)


class DAGNode:
    """Node in a DAG representing a task."""

    def __init__(self, node_id: str, task: Any, metadata: Optional[Dict] = None):
        """
        Initialize DAG node.

        Args:
            node_id: Unique node identifier
            task: Task object
            metadata: Optional metadata
        """
        self.node_id = node_id
        self.task = task
        self.metadata = metadata or {}
        self.dependencies: Set[str] = set()
        self.dependents: Set[str] = set()

    def add_dependency(self, node_id: str) -> None:
        """Add a dependency (this node depends on another)."""
        self.dependencies.add(node_id)

    def add_dependent(self, node_id: str) -> None:
        """Add a dependent (another node depends on this)."""
        self.dependents.add(node_id)

    def __repr__(self) -> str:
        """String representation."""
        return f"DAGNode(id={self.node_id}, deps={len(self.dependencies)}, dependents={len(self.dependents)})"


class DAG:
    """Directed Acyclic Graph for workflow dependency management."""

    def __init__(self):
        """Initialize DAG."""
        self.nodes: Dict[str, DAGNode] = {}

    def add_node(self, node: DAGNode) -> None:
        """
        Add a node to the DAG.

        Args:
            node: DAGNode to add
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists in DAG")

        self.nodes[node.node_id] = node
        logger.debug(f"Added node {node.node_id} to DAG")

    def add_edge(self, from_id: str, to_id: str) -> None:
        """
        Add an edge (dependency) between two nodes.

        Args:
            from_id: Source node ID (dependency)
            to_id: Target node ID (dependent)

        Raises:
            ValueError: If nodes don't exist
            WorkflowValidationError: If edge would create a cycle
        """
        if from_id not in self.nodes:
            raise ValueError(f"Node {from_id} not found in DAG")
        if to_id not in self.nodes:
            raise ValueError(f"Node {to_id} not found in DAG")

        # Check if adding this edge would create a cycle
        if self._would_create_cycle(from_id, to_id):
            raise WorkflowValidationError(
                f"Adding edge {from_id} -> {to_id} would create a cycle",
                details={"from": from_id, "to": to_id},
            )

        self.nodes[to_id].add_dependency(from_id)
        self.nodes[from_id].add_dependent(to_id)

        logger.debug(f"Added edge {from_id} -> {to_id}")

    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """
        Check if adding an edge would create a cycle.

        Args:
            from_id: Source node ID
            to_id: Target node ID

        Returns:
            True if cycle would be created
        """
        # If there's already a path from to_id to from_id, adding the edge would create a cycle
        return self._has_path(to_id, from_id)

    def _has_path(self, start_id: str, end_id: str) -> bool:
        """
        Check if there's a path from start to end.

        Args:
            start_id: Starting node ID
            end_id: Ending node ID

        Returns:
            True if path exists
        """
        if start_id == end_id:
            return True

        visited = set()
        stack = [start_id]

        while stack:
            node_id = stack.pop()
            if node_id in visited:
                continue

            visited.add(node_id)

            if node_id == end_id:
                return True

            node = self.nodes.get(node_id)
            if node:
                for dependent in node.dependents:
                    if dependent not in visited:
                        stack.append(dependent)

        return False

    def topological_sort(self) -> List[str]:
        """
        Perform topological sort on the DAG.

        Returns:
            List of node IDs in topological order

        Raises:
            WorkflowValidationError: If DAG contains a cycle
        """
        # Calculate in-degree for each node
        in_degree = {node_id: len(node.dependencies) for node_id, node in self.nodes.items()}

        # Find all nodes with no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort queue for deterministic ordering
            queue.sort()
            node_id = queue.pop(0)
            result.append(node_id)

            # Reduce in-degree for dependent nodes
            node = self.nodes[node_id]
            for dependent in node.dependents:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # If we didn't visit all nodes, there's a cycle
        if len(result) != len(self.nodes):
            raise WorkflowValidationError(
                "DAG contains a cycle",
                details={"nodes_visited": len(result), "total_nodes": len(self.nodes)},
            )

        logger.debug(f"Topological sort: {result}")
        return result

    def get_execution_levels(self) -> List[List[str]]:
        """
        Get nodes grouped by execution level (for parallel execution).

        Returns:
            List of lists, where each inner list contains nodes that can be executed in parallel
        """
        levels = []
        remaining = set(self.nodes.keys())
        completed = set()

        while remaining:
            # Find all nodes whose dependencies are completed
            level = []
            for node_id in remaining:
                node = self.nodes[node_id]
                if node.dependencies.issubset(completed):
                    level.append(node_id)

            if not level:
                raise WorkflowValidationError(
                    "Cannot determine execution levels - possible cycle detected"
                )

            levels.append(sorted(level))  # Sort for deterministic ordering
            completed.update(level)
            remaining -= set(level)

        logger.debug(f"Execution levels: {levels}")
        return levels

    def get_node(self, node_id: str) -> Optional[DAGNode]:
        """
        Get a node by ID.

        Args:
            node_id: Node identifier

        Returns:
            DAGNode or None
        """
        return self.nodes.get(node_id)

    def validate(self) -> bool:
        """
        Validate the DAG.

        Returns:
            True if valid

        Raises:
            WorkflowValidationError: If validation fails
        """
        # Check for cycles by attempting topological sort
        try:
            self.topological_sort()
        except WorkflowValidationError:
            raise

        # Validate that all referenced dependencies exist
        for node_id, node in self.nodes.items():
            for dep_id in node.dependencies:
                if dep_id not in self.nodes:
                    raise WorkflowValidationError(
                        f"Node {node_id} has dependency {dep_id} which doesn't exist",
                        details={"node": node_id, "missing_dependency": dep_id},
                    )

        logger.debug("DAG validation successful")
        return True

    def __len__(self) -> int:
        """Get number of nodes."""
        return len(self.nodes)

    def __repr__(self) -> str:
        """String representation."""
        return f"DAG(nodes={len(self.nodes)})"
