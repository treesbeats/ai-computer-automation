"""Tests for AI modules."""

import pytest
from unittest.mock import Mock, patch
from ai_automation.ai.client import AIClient, create_ai_client
from ai_automation.ai.decision import AIDecisionMaker


class TestAIClient:
    """Tests for AI client functionality."""

    def test_create_ai_client_no_key(self):
        """Test creating client without API key."""
        with pytest.raises(ValueError):
            create_ai_client("openai", api_key=None)

    def test_create_ai_client_invalid_provider(self):
        """Test creating client with invalid provider."""
        with pytest.raises(ValueError):
            create_ai_client("invalid_provider", api_key="test_key")


class TestAIDecisionMaker:
    """Tests for AI decision maker."""

    def test_initialization(self):
        """Test decision maker initialization."""
        mock_client = Mock(spec=AIClient)
        decision_maker = AIDecisionMaker(mock_client)
        assert decision_maker.client == mock_client

    def test_should_proceed_yes(self):
        """Test should_proceed with yes response."""
        mock_client = Mock(spec=AIClient)
        mock_client.complete.return_value = "Yes, we should proceed because..."

        decision_maker = AIDecisionMaker(mock_client)
        result = decision_maker.should_proceed("Test context")

        assert result is True
        mock_client.complete.assert_called_once()

    def test_should_proceed_no(self):
        """Test should_proceed with no response."""
        mock_client = Mock(spec=AIClient)
        mock_client.complete.return_value = "No, we should not proceed because..."

        decision_maker = AIDecisionMaker(mock_client)
        result = decision_maker.should_proceed("Test context")

        assert result is False

    def test_should_proceed_error(self):
        """Test should_proceed with error."""
        mock_client = Mock(spec=AIClient)
        mock_client.complete.side_effect = Exception("API Error")

        decision_maker = AIDecisionMaker(mock_client)
        result = decision_maker.should_proceed("Test context")

        # Should default to False on error for safety
        assert result is False

    def test_choose_option(self):
        """Test choose_option method."""
        mock_client = Mock(spec=AIClient)
        mock_client.complete.return_value = "I recommend option2 because..."

        decision_maker = AIDecisionMaker(mock_client)
        options = ["option1", "option2", "option3"]
        result = decision_maker.choose_option("Which option?", options)

        assert result in options
        mock_client.complete.assert_called_once()

    def test_generate_action_plan(self):
        """Test generate_action_plan method."""
        mock_client = Mock(spec=AIClient)
        mock_client.complete.return_value = """
        1. First step
        2. Second step
        3. Third step
        """

        decision_maker = AIDecisionMaker(mock_client)
        result = decision_maker.generate_action_plan("Test goal")

        assert isinstance(result, list)
        assert len(result) > 0
        mock_client.complete.assert_called_once()

    def test_evaluate_outcome(self):
        """Test evaluate_outcome method."""
        mock_client = Mock(spec=AIClient)
        mock_client.complete.return_value = "Success: yes\nConfidence: 85%\nReasoning: ..."

        decision_maker = AIDecisionMaker(mock_client)
        result = decision_maker.evaluate_outcome(
            "Test action", "Test result", "Expected outcome"
        )

        assert isinstance(result, dict)
        assert "success" in result
        assert "confidence" in result
        assert "reasoning" in result
        mock_client.complete.assert_called_once()
