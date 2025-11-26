"""AI-powered decision making for automation."""

from typing import Optional, List, Dict, Any
import logging
from ai_automation.ai.client import AIClient

logger = logging.getLogger(__name__)


class AIDecisionMaker:
    """Uses AI to make decisions in automation workflows."""

    def __init__(self, client: AIClient):
        """
        Initialize decision maker.

        Args:
            client: AI client instance
        """
        self.client = client
        logger.info("Initialized AI decision maker")

    def should_proceed(self, context: str, criteria: Optional[str] = None) -> bool:
        """
        Ask AI whether to proceed with an action.

        Args:
            context: Description of the current situation
            criteria: Optional decision criteria

        Returns:
            True if should proceed, False otherwise
        """
        prompt = f"Context: {context}\n\n"
        if criteria:
            prompt += f"Criteria: {criteria}\n\n"
        prompt += "Should we proceed with this action? Answer only 'yes' or 'no' and briefly explain why."

        try:
            response = self.client.complete(prompt)
            decision = "yes" in response.lower()
            logger.info(f"AI decision: {'proceed' if decision else 'do not proceed'}")
            logger.debug(f"AI reasoning: {response}")
            return decision
        except Exception as e:
            logger.error(f"Error getting AI decision: {e}")
            # Default to not proceeding on error for safety
            return False

    def choose_option(
        self, question: str, options: List[str], context: Optional[str] = None
    ) -> str:
        """
        Ask AI to choose from multiple options.

        Args:
            question: The question to ask
            options: List of available options
            context: Optional additional context

        Returns:
            Selected option
        """
        prompt = f"Question: {question}\n\n"
        if context:
            prompt += f"Context: {context}\n\n"
        prompt += f"Options:\n"
        for i, option in enumerate(options, 1):
            prompt += f"{i}. {option}\n"
        prompt += "\nChoose the best option and explain your reasoning briefly."

        try:
            response = self.client.complete(prompt)
            logger.info(f"AI choice made from {len(options)} options")
            logger.debug(f"AI response: {response}")

            # Try to extract the chosen option
            for option in options:
                if option.lower() in response.lower():
                    return option

            # Default to first option if unclear
            return options[0]
        except Exception as e:
            logger.error(f"Error getting AI choice: {e}")
            return options[0]

    def generate_action_plan(
        self, goal: str, constraints: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate a step-by-step action plan.

        Args:
            goal: The goal to achieve
            constraints: Optional list of constraints

        Returns:
            List of action steps
        """
        prompt = f"Goal: {goal}\n\n"
        if constraints:
            prompt += "Constraints:\n"
            for constraint in constraints:
                prompt += f"- {constraint}\n"
            prompt += "\n"
        prompt += "Generate a step-by-step action plan to achieve this goal. List each step on a new line starting with a number."

        try:
            response = self.client.complete(prompt)
            logger.info(f"AI generated action plan for: {goal}")

            # Parse steps from response
            steps = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove numbering and clean up
                    step = line.lstrip("0123456789.-) ").strip()
                    if step:
                        steps.append(step)

            return steps if steps else [response]
        except Exception as e:
            logger.error(f"Error generating action plan: {e}")
            return []

    def evaluate_outcome(
        self, action: str, result: str, expected: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate whether an action outcome was successful.

        Args:
            action: The action that was taken
            result: The observed result
            expected: Optional expected outcome

        Returns:
            Dictionary with 'success' (bool), 'confidence' (float), and 'reasoning' (str)
        """
        prompt = f"Action taken: {action}\n"
        prompt += f"Observed result: {result}\n"
        if expected:
            prompt += f"Expected outcome: {expected}\n"
        prompt += "\nEvaluate if this action was successful. Respond with:\n"
        prompt += "1. Success: yes or no\n"
        prompt += "2. Confidence: 0-100%\n"
        prompt += "3. Brief reasoning"

        try:
            response = self.client.complete(prompt)
            logger.info(f"AI evaluated outcome for action: {action}")

            # Parse response
            success = "success: yes" in response.lower() or "successful" in response.lower()

            # Try to extract confidence
            confidence = 0.5  # Default
            if "confidence:" in response.lower():
                try:
                    conf_text = response.lower().split("confidence:")[1].split()[0]
                    confidence = float(conf_text.strip("%")) / 100
                except:
                    pass

            return {
                "success": success,
                "confidence": confidence,
                "reasoning": response,
            }
        except Exception as e:
            logger.error(f"Error evaluating outcome: {e}")
            return {
                "success": False,
                "confidence": 0.0,
                "reasoning": f"Error: {e}",
            }
