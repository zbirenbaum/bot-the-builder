from anthropic import Anthropic
import os
import json
from typing import List, Dict, Optional, Union, Any, Literal
import argparse
import weave
from enum import Enum, auto
import openai
from agents.helpers.backend import BackendType, AgentBackend

class RequirementResolverAgent:
    """
    An agent that uses LLMs to analyze a task description
    and determine the necessary pip libraries to accomplish the task.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 backend_type: BackendType = BackendType.ANTHROPIC,
                 model: Optional[str] = None):
        """
        Initialize the RequirementResolverAgent.
        
        Args:
            api_key: API key for the selected backend. If None, will try to get from environment variable.
            backend_type: The type of LLM backend to use (default: ANTHROPIC)
            model: The specific model to use (default: None, will use backend default)
        """
        self.system_prompt = """You are a specialized AI assistant focused on determining the necessary Python libraries needed to accomplish a given task.

Your job is to:
1. Analyze the task description carefully
2. Identify the Python libraries that would be required to implement the task
3. For each library, provide:
   - The exact pip package name
   - A brief description of why it's needed for this task
   - The recommended version (if applicable)
   - Whether it's essential or optional

Return your response in the following JSON format:
{
  "libraries": [
    {
      "name": "package-name",
      "description": "Why this library is needed",
      "version": "recommended-version or 'latest'",
      "essential": true/false
    },
    ...
  ],
  "reasoning": "Brief explanation of your overall thought process"
}

Be thorough but practical - include all necessary libraries but avoid unnecessary ones.
"""
        # Initialize the backend
        self.backend = AgentBackend(
            backend_type=backend_type,
            system_prompt=self.system_prompt,
            api_key=api_key,
            model=model
        )

    @weave.op
    def resolve_requirements(self, task_description: str) -> Dict:
        """
        Analyze a task description and determine the necessary pip libraries.
        
        Args:
            task_description: A description of the task to be accomplished
            
        Returns:
            A dictionary containing the resolved requirements and metadata
        """
        try:
            # Generate response using the backend
            prompt = f"Please analyze the following task and determine the necessary Python libraries needed:\n\n{task_description}"
            response_text = self.backend.generate(prompt)
            
            # Find JSON content (it might be wrapped in ```json blocks)
            json_content = response_text
            if "```json" in response_text:
                json_blocks = response_text.split("```json")
                if len(json_blocks) > 1:
                    json_content = json_blocks[1].split("```")[0].strip()
            elif "```" in response_text:
                json_blocks = response_text.split("```")
                if len(json_blocks) > 1:
                    json_content = json_blocks[1].strip()
            
            # Parse the JSON response
            requirements = json.loads(json_content)
            
            # Add metadata
            result = {
                "success": True,
                "task_description": task_description,
                "requirements": requirements
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "task_description": task_description,
                "error": str(e)
            }
    
    def generate_requirements_txt(self, resolved_requirements: Dict, output_file: str = "requirements.txt") -> str:
        """
        Generate a requirements.txt file from the resolved requirements.
        
        Args:
            resolved_requirements: The dictionary returned by resolve_requirements
            output_file: Path to the output requirements.txt file
            
        Returns:
            The content of the generated requirements.txt file
        """
        if not resolved_requirements.get("success", False):
            raise ValueError(f"Cannot generate requirements.txt from failed resolution: {resolved_requirements.get('error')}")
        
        requirements = resolved_requirements.get("requirements", {})
        libraries = requirements.get("libraries", [])
        
        # Generate requirements.txt content
        lines = [
            "# Requirements for: " + resolved_requirements.get("task_description", "Unknown task"),
            "# Generated automatically by RequirementResolverAgent",
            ""
        ]
        
        # Add essential libraries first
        essential_libs = [lib for lib in libraries if lib.get("essential", True)]
        if essential_libs:
            lines.append("# Essential libraries")
            for lib in essential_libs:
                version_spec = f"=={lib['version']}" if lib.get("version") and lib["version"] != "latest" else ""
                lines.append(f"{lib['name']}{version_spec}")
            lines.append("")
        
        # Add optional libraries
        optional_libs = [lib for lib in libraries if not lib.get("essential", True)]
        if optional_libs:
            lines.append("# Optional libraries")
            for lib in optional_libs:
                version_spec = f"=={lib['version']}" if lib.get("version") and lib["version"] != "latest" else ""
                lines.append(f"{lib['name']}{version_spec}  # Optional")
        
        # Write to file
        content = "\n".join(lines)
        if output_file:
            with open(output_file, "w") as f:
                f.write(content)
        
        return content

def main():
    parser = argparse.ArgumentParser(description="Resolve Python package requirements for a given task")
    parser.add_argument("task", help="Description of the task to accomplish")
    parser.add_argument("--output", "-o", default="requirements.txt", help="Output file for requirements")
    parser.add_argument("--api-key", help="API key (optional if set as environment variable)")
    parser.add_argument("--backend", choices=["anthropic", "openai"], default="anthropic", 
                        help="LLM backend to use (default: anthropic)")
    parser.add_argument("--model", help="Specific model to use (optional)")
    
    args = parser.parse_args()
    
    # Convert string backend choice to enum
    backend_type = BackendType.ANTHROPIC if args.backend == "anthropic" else BackendType.OPENAI
    
    resolver = RequirementResolverAgent(
        api_key=args.api_key,
        backend_type=backend_type,
        model=args.model
    )
    resolved = resolver.resolve_requirements(args.task)
    
    if resolved["success"]:
        requirements_txt = resolver.generate_requirements_txt(resolved, args.output)
        print(f"Requirements successfully resolved and written to {args.output}")
        print("\nResolved libraries:")
        for lib in resolved["requirements"]["libraries"]:
            essential = "Essential" if lib.get("essential", True) else "Optional"
            print(f"- {lib['name']} ({essential}): {lib['description']}")
    else:
        print(f"Error resolving requirements: {resolved.get('error')}")

if __name__ == "__main__":
    main()