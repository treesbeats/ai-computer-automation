"""AI client implementations for various providers."""

from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class AIClient(ABC):
    """Abstract base class for AI clients."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion from the AI model.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        pass


class OpenAIClient(AIClient):
    """OpenAI API client."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"Initialized OpenAI client with model: {model}")

    def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion from OpenAI.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise


class AnthropicClient(AIClient):
    """Anthropic (Claude) API client."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-sonnet)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"Initialized Anthropic client with model: {model}")

    def complete(self, prompt: str, **kwargs) -> str:
        """
        Generate a completion from Anthropic.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        try:
            response = self.client.messages.create(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic completion error: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        try:
            response = self.client.messages.create(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise


def create_ai_client(
    provider: str = "openai",
    api_key: Optional[str] = None,
    **kwargs
) -> AIClient:
    """
    Factory function to create an AI client.

    Args:
        provider: AI provider ('openai' or 'anthropic')
        api_key: API key for the provider
        **kwargs: Additional parameters for the client

    Returns:
        AIClient instance

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    if not api_key:
        raise ValueError(f"API key required for {provider}")

    provider = provider.lower()

    if provider == "openai":
        return OpenAIClient(api_key=api_key, **kwargs)
    elif provider == "anthropic":
        return AnthropicClient(api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
