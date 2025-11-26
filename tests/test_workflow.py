"""Tests for workflow module."""

import pytest
from ai_automation.workflow import DAG, DAGNode, Workflow, WorkflowEngine
from ai_automation.core.enhanced_task import EnhancedTask
from ai_automation.exceptions import WorkflowValidationError


class DummyTask(EnhancedTask):
    """Dummy task for testing."""

    def _run(self):
        self.result = f"Executed {self.name}"


class TestDAG:
    """Tests for DAG class."""

    def test_create_dag(self):
        """Test DAG creation."""
        dag = DAG()
        assert len(dag) == 0

    def test_add_node(self):
        """Test adding nodes to DAG."""
        dag = DAG()
        task = DummyTask("task1")
        node = DAGNode("task1", task)
        dag.add_node(node)
        assert len(dag) == 1

    def test_add_edge(self):
        """Test adding edges to DAG."""
        dag = DAG()
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")

        node1 = DAGNode("task1", task1)
        node2 = DAGNode("task2", task2)

        dag.add_node(node1)
        dag.add_node(node2)
        dag.add_edge("task1", "task2")

        assert "task1" in dag.nodes["task2"].dependencies

    def test_detect_cycle(self):
        """Test cycle detection."""
        dag = DAG()
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")

        node1 = DAGNode("task1", task1)
        node2 = DAGNode("task2", task2)

        dag.add_node(node1)
        dag.add_node(node2)
        dag.add_edge("task1", "task2")

        # This should raise an error (creates a cycle)
        with pytest.raises(WorkflowValidationError):
            dag.add_edge("task2", "task1")

    def test_topological_sort(self):
        """Test topological sort."""
        dag = DAG()
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")
        task3 = DummyTask("task3")

        for i, task in enumerate([task1, task2, task3], 1):
            node = DAGNode(f"task{i}", task)
            dag.add_node(node)

        dag.add_edge("task1", "task2")
        dag.add_edge("task2", "task3")

        order = dag.topological_sort()
        assert order.index("task1") < order.index("task2")
        assert order.index("task2") < order.index("task3")

    def test_execution_levels(self):
        """Test execution level grouping."""
        dag = DAG()

        # Create a diamond pattern
        # task1 -> task2, task3 -> task4
        for i in range(1, 5):
            task = DummyTask(f"task{i}")
            node = DAGNode(f"task{i}", task)
            dag.add_node(node)

        dag.add_edge("task1", "task2")
        dag.add_edge("task1", "task3")
        dag.add_edge("task2", "task4")
        dag.add_edge("task3", "task4")

        levels = dag.get_execution_levels()
        assert len(levels) == 3
        assert levels[0] == ["task1"]
        assert set(levels[1]) == {"task2", "task3"}
        assert levels[2] == ["task4"]


class TestWorkflow:
    """Tests for Workflow class."""

    def test_create_workflow(self):
        """Test workflow creation."""
        workflow = Workflow("test_workflow")
        assert workflow.name == "test_workflow"

    def test_add_task(self):
        """Test adding tasks to workflow."""
        workflow = Workflow("test_workflow")
        task = DummyTask("task1")
        task_id = workflow.add_task(task)
        assert task_id in workflow.tasks

    def test_add_task_with_dependencies(self):
        """Test adding task with dependencies."""
        workflow = Workflow("test_workflow")
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")

        id1 = workflow.add_task(task1)
        id2 = workflow.add_task(task2, depends_on=[id1])

        assert id1 in workflow.tasks[id2].dependencies

    def test_validate_workflow(self):
        """Test workflow validation."""
        workflow = Workflow("test_workflow")
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")

        id1 = workflow.add_task(task1)
        id2 = workflow.add_task(task2, depends_on=[id1])

        # Should validate successfully
        assert workflow.validate()


class TestWorkflowEngine:
    """Tests for WorkflowEngine class."""

    def test_create_engine(self):
        """Test engine creation."""
        engine = WorkflowEngine(max_workers=2)
        assert engine.max_workers == 2
        engine.shutdown()

    def test_execute_sequential(self):
        """Test sequential execution."""
        workflow = Workflow("test_workflow")
        task1 = DummyTask("task1")
        task2 = DummyTask("task2")

        workflow.add_task(task1)
        workflow.add_task(task2, depends_on=[task1.task_id])

        engine = WorkflowEngine()
        results = engine.execute(workflow, parallel=False)

        assert results["success"]
        assert results["completed_tasks"] == 2
        engine.shutdown()
