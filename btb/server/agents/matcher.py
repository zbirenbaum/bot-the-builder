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

class ToolMatcherAgent:
    def __init__(self, backend: BackendType = BackendType.ANTHROPIC):
        self.system_prompt = """You are a specialized code matching assistant focused on determining if a tool with a given description can be used to accomplish another task described to you.
Your primary role is to:
1. Take in code blocks and description of the code from a previous response
2. Take in a second description of a task and determine if the code from the previous response can be used to accomplish the task

When generating tool code, always return response in the following format:
# START_MATCH
TRUE or FALSE
# END_MATCH

example 1:
# START_MATCH
TRUE
# END_MATCH

example 2:
# START_MATCH
FALSE
# END_MATCH
"""
        self.backend = AgentBackend(backend, self.system_prompt)

    @weave.op
    def match_tool(self, task_description: str, tool_description: str, tool_implementation: str, load_file_name: str | None = None, save_file_name: str | None = None) -> str:
        print(f"Task description: {task_description}")
        print(f"Matching tool: {tool_description}")
        print(f"Tool implementation: {tool_implementation}")
        if load_file_name:
            try:
                with open(load_file_name, "r") as f:
                    return f.read()
            except Exception as e:
                return f"Failed to load file: {str(e)}"

        try:
            prompt = f"""
Task description: {task_description}
Tool description: {tool_description}
Tool Implementation: {tool_implementation}

Can this tool be used to accomplish the task?
"""
            with_main_fn = self.backend.generate(prompt)
        except Exception as e:
            return f"Failed to generate main function: {str(e)}"

        match = parse_marked_blocks(Marker.MATCH, with_main_fn)
        if save_file_name:
            with open(save_file_name, "w") as f:
                f.write(match)
        return match
