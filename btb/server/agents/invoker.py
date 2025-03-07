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

class ToolInvocationAgent:
    def __init__(self, backend: BackendType = BackendType.ANTHROPIC):
        self.system_prompt = """You are a specialized code generation assistant focused on creating command line code for AI agents. 
Your primary role is to:
1. Take in a tool id, description, and implementation
2. Take in a task description
3. Create a command line invocation of the tool with arguments determined by information in the task

When generating the code:
1. Never set environment variables or pass them as arguments anywhere in the command
2. Always name the script to run the tool by its id
2. Always return response in the following format:
# START_IMPLEMENTATION
command line invocation
# END_IMPLEMENTATION

Example:
Input Prompt:
ID: abc-def-ghi
TASK: Print 'hello world'
ARGUMENTS: message
ARGUMENT_TYPES: str
SUMMARY: Print a string
IMPLEMENTATION: str

Output:
# START_IMPLEMENTATION
python abc-def-ghi.py "hello world"
# END_IMPLEMENTATION
"""
        self.backend = AgentBackend(backend, self.system_prompt)

    # def format_command(self, id: str, command: str) -> str:
    #     parts = command.split(' ')
    #     return parts[0] + ' ' + id + '.py ' + ' '.join(parts[1:])

    @weave.op
    def generate_invocation(
        self,
        id: str,
        task: str,
        arguments: str, 
        argument_types: str,
        summary: str,
        implementation: str,
        load_file_name: str | None = None,
        save_file_name: str | None = None
    ) -> str:
        if load_file_name:
            try:
                with open(load_file_name, "r") as f:
                    command_implementation = f.read()
                    return parse_marked_blocks(Marker.IMPLEMENTATION, command_implementation)
            except Exception as e:
                return f"Failed to load file: {str(e)}"

        prompt = '\n'.join([
            f"ID: {id}",
            f"TASK: {task}",
            f"ARGUMENTS: {arguments}",
            f"ARGUMENT_TYPES: {argument_types}",
            f"SUMMARY: {summary}",
            f"implementation: {implementation}",
        ])
        try:
            command_implementation = self.backend.generate(prompt)
            if save_file_name:
                with open(save_file_name, "w") as f:
                    f.write(command_implementation)
        except Exception as e:
            return f"Failed to generate main function: {str(e)}"

        return parse_marked_blocks(Marker.IMPLEMENTATION, command_implementation)
