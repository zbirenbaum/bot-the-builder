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

class ToolFormatterAgent:
    def __init__(self, backend: BackendType = BackendType.ANTHROPIC):
        self.system_prompt = """You are a specialized code generation assistant focused on creating tool implementations for AI agents. 
Your primary role is to:
1. Take in code blocks from a previous response
2. Add an if __name__ == "__main__": statement to the code block that parses command line arguments and calls the tool with the correct arguments
3. Create a usage example for the tool. The usage example should only include a command line invocation of the tool.
4. Arguments in the usage example should be formatted as --argument_name=argument_value
5. Never take API keys or other sensitive information as arguments, always load them from environment variables
6. Always include the full implementation code for the tool provided in the prompt within your response
7. Never add any extra information to the output. Always return the value as it was output by the tool.
8. The value should be parsable by passing the output to `eval(output)`

When generating tool code, always return response in the following format:
# START_IMPLEMENTATION
Code Block
# END_IMPLEMENTATION
"""
        self.backend = AgentBackend(backend, self.system_prompt)

    @weave.op
    def generate_main_function(self, code_implementation: str, load_file_name: str | None = None, save_file_name: str | None = None) -> str:
        if load_file_name:
            try:
                with open(load_file_name, "r") as f:
                    return f.read()
            except Exception as e:
                return f"Failed to load file: {str(e)}"

        try:
            with_main_fn = self.backend.generate(code_implementation)
        except Exception as e:
            return f"Failed to generate main function: {str(e)}"

        implementation = parse_marked_blocks(Marker.IMPLEMENTATION, with_main_fn)
        if save_file_name:
            with open(save_file_name, "w") as f:
                f.write(implementation)
        return implementation
