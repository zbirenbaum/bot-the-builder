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

class ToolSummaryAgent:
    def __init__(self, backend: BackendType = BackendType.ANTHROPIC):
        self.system_prompt = """You are a specialized code designer
Your primary role is to:
1. Take in a specific task description
2. Summarize the specific task description into a more general problem statement
3. Keep specific APIs or services such as Discord, Google, Telegram, etc. in the summary.
4. Specify the format of the return value of the task.

When generating description, always return response in the following format:
# START_SUMMARY
Summary
# END_SUMMARY

example:
Input: Find the top 10 results for 'python' in google

Output:
# START_SUMMARY
Find the top N results in google given a specific number N and a search query. Return a List of URLs
# END_SUMMARY
"""
        self.backend = AgentBackend(backend, self.system_prompt)

    @weave.op
    def summarize(self, task_description: str, load_file_name: str | None = None, save_file_name: str | None = None) -> str:
        if load_file_name:
            try:
                with open(load_file_name, "r") as f:
                    return f.read()
            except Exception as e:
                return f"Failed to load file: {str(e)}"

        try:
            with_main_fn = self.backend.generate(task_description)
        except Exception as e:
            return f"Failed to generate main function: {str(e)}"

        summary = parse_marked_blocks(Marker.SUMMARY, with_main_fn)
        if save_file_name:
            with open(save_file_name, "w") as f:
                f.write(summary)
        return summary
