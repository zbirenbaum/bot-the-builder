from anthropic import Anthropic
import os
from anthropic.types.content_block import ContentBlock
import weave
import dotenv
import re
from mdextractor import extract_md_blocks
from typing import Dict, Optional, List
from enum import Enum

from .helpers.marker import Marker, parse_marked_blocks
from .helpers.backend import BackendType, AgentBackend

dotenv.load_dotenv()

class ToolGeneratorAgent:
    def __init__(self, backend: BackendType = BackendType.ANTHROPIC):
        self.system_prompt = """You are a specialized code generation assistant focused on creating tool implementations for AI agents. 
Your primary role is to:
1. Generate clean, well-documented tool code
2. Follow best practices and include proper error handling
3. Ensure tools are easily integrable with AI agent systems
4. Include type hints and docstrings
5. Never take API keys or other sensitive information as arguments, always load them from environment variables
6. Return a type matching what is described in the summary
7. Do not transform or filter data returned by a web api unless explicitly asked to do so

Requirements:
- Required dependencies
- Clear documentation
- Error handling
- Return type specifications
- Usage examples
- Output value can by parsed to a type with 'eval(output)'

When generating tool code, always return response in the following format:
# START_IMPLEMENTATION
Code Block
# END_IMPLEMENTATION

# START_DEPENDENCIES
List of comma separated pip libraries to install. If none write NONE
# END_DEPENDENCIES

# START_ARGUMENTS
List of comma separated arguments to pass to the tool
# END_ARGUMENTS

# START_ARGUMENT_TYPES
List of comma separated argument types to pass to the tool
# END_ARGUMENT_TYPES

# START_ENV_VARIABLES
List of comma separated environment variables to load. If none, write NONE
# END_ENV_VARIABLES
"""
        self.backend = AgentBackend(backend, self.system_prompt)

    @weave.op
    def generate_tool_code(self,
                          tool_description: str,
                          language: str = "python",
                          save_file_name: str | None = None,
                          load_file_name: str | None = None) -> Dict[str, str]:
        """
        Generate code for a new tool based on the description.

        Args:
            tool_description: Detailed description of the tool's purpose and requirements
            language: Programming language to use (default: python)
        Returns:
            Dict containing generated code and optionally test code
        """
        prompt = f"""Please generate {language} code for a tool with the following description:
{tool_description}

The code should be production-ready, well-documented, and include error handling.
"""

        try:
            text = ""
            if load_file_name:
                with open(load_file_name, "r") as f:
                    text = f.read()
            else:
                text = self.backend.generate(prompt)
                with open(save_file_name, "w") as f:
                    f.write(text)
            code_content = {}
            # Extract code blocks from the response
            for marker in Marker:
                code_content[marker.name] = parse_marked_blocks(marker, text)

            return {
                "success": str(True),
                "implementation": code_content.get(Marker.IMPLEMENTATION.name, ""),
                "dependencies": code_content.get(Marker.DEPENDENCIES.name, ""),
                "arguments": code_content.get(Marker.ARGUMENTS.name, ""),
                "argument_types": code_content.get(Marker.ARGUMENT_TYPES.name, ""),
                "env_variables": code_content.get(Marker.ENV_VARIABLES.name, "")
            }

        except Exception as e:
            return {
                "success": str(False),
                "error": f"Failed to generate tool code: {str(e)}"
            }

def main():
    # Example usage
    generator = ToolGeneratorAgent()

    tool_description = """Create a tool that can summarize a given text using the OpenAI API.
    The tool should:
    - Accept text input
    - Have a maximum token limit
    - Return a concise summary
    - Handle API errors gracefully"""

    result = generator.generate_tool_code(
        tool_description=tool_description,
        include_tests=True
    )

    if result["success"]:
        print("Generated Implementation:")
        print(result["implementation"])
        if result["tests"]:
            print("\nGenerated Tests:")
            print(result["tests"])
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
