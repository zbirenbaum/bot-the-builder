from anthropic import Anthropic
from anthropic.types.content_block import ContentBlock
import weave
import dotenv
from mdextractor import extract_md_blocks
from typing import Dict, Optional, List
from enum import Enum
from .helpers.marker import Marker, parse_marked_blocks
from .helpers.backend import BackendType, AgentBackend

dotenv.load_dotenv()
# Take in an exception, implementation code, and invocation command
# Return an explanation of the issue and the requirments to fix it

class ToolFormatterAgent:
    def __init__(self, backend: BackendType = BackendType.ANTHROPIC):
        self.system_prompt = """You are a specialized code generation assistant focused on debuggingtool implementations for AI agents. 
Your primary role is to:
1. Take in code blocks from a previous response, an exception, and an invocation command
2. Return an explanation of the issue and the requirments to fix it

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
