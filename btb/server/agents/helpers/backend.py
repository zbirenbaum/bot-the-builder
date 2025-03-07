from enum import Enum, auto
from typing import Optional
import os
from anthropic import Anthropic
import openai

class BackendType(Enum):
    """Enum representing the available LLM backend providers."""
    ANTHROPIC = auto()
    OPENAI = auto()

class AgentBackend:
    """
    A flexible backend class that supports multiple LLM providers.
    Currently supports OpenAI and Anthropic APIs.
    """
    
    def __init__(self, 
                 backend_type: BackendType, 
                 system_prompt: str,
                 api_key: Optional[str] = None,
                 model: Optional[str] = None):
        """
        Initialize the AgentBackend.

        Args:
            backend_type: The type of LLM backend to use (OpenAI or Anthropic)
            system_prompt: The system prompt to use for the LLM
            api_key: API key for the selected backend. If None, will try to get from environment variables
            model: The specific model to use. If None, will use a default model for the selected backend
        """
        self.backend_type = backend_type
        self.system_prompt = system_prompt

        # Set up the appropriate client based on backend type
        if backend_type == BackendType.ANTHROPIC:
            self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API key must be provided or set as ANTHROPIC_API_KEY environment variable")
            self.client = Anthropic(api_key=self.api_key)
            self.model = model or "claude-3-sonnet-20240229"

        elif backend_type == BackendType.OPENAI:
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model = model or "gpt-4-turbo"

        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

    def generate(self, 
                prompt: str, 
                max_tokens: int = 4096, 
                temperature: float = 0) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for generation (0-1)
            
        Returns:
            The generated text response
        """
        if self.backend_type == BackendType.ANTHROPIC:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
            
        elif self.backend_type == BackendType.OPENAI:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        
        else:
            raise ValueError(f"Unsupported backend type: {self.backend_type}")
