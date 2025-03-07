from .agents.generator import ToolGeneratorAgent
from .agents import ToolFormatterAgent, ToolInvocationAgent, ToolGeneratorAgent, ToolSummaryAgent, ToolMatcherAgent
from .agents.helpers.db_helper import DBAdapter
import weave
import uuid
import argparse
from dotenv import load_dotenv
load_dotenv()

weave.init("wandb/zach-agent-project-v1")

class ToolAgentServer():
    def __init__(self, clear_db=False):
        if clear_db:
            db = DBAdapter()
            db.clear_db()
        self.run_server()

    @weave.op
    def handle_tool_request(self, task_description: str):
        generator = ToolGeneratorAgent()
        formatter = ToolFormatterAgent()
        invoker = ToolInvocationAgent()
        matcher = ToolMatcherAgent()
        summarizer = ToolSummaryAgent()
        db_helper = DBAdapter()

        @weave.op
        def generate_new_tool(summary: str):
            id = str(uuid.uuid4())
            print(f"Generating new tool: {summary}")
            generated = generator.generate_tool_code(summary, "python", save_file_name=f"save_runs/generate_{id}.py")
            print(generated)
            print(f"Converting implementation to main function")
            try:
                generated['implementation'] = formatter.generate_main_function(generated["implementation"], save_file_name=f"save_runs/formatted_{id}.py")
            except Exception as e:
                print('exception:', e)
            print(f"Adding tool to database")

            db_helper.add_tool(
                id,
                summary,
                generated.get("arguments"),
                generated.get("argument_types"),
                generated.get("env_variables"),
                generated.get("command"),
                generated.get("implementation"),
                generated.get("dependencies")
            )

            return db_helper.get_tool(id)

        def try_retrieve_tool(summary: str):
            results = db_helper.query(summary)
            ids = results['ids'][0]
            print(f"IDs: {ids}")
            if len(ids) > 0:
                id = ids[0]
                tool = db_helper.get_tool(id)
                # Match the tool to the task description
                match = matcher.match_tool(summary, tool["description"], tool["implementation"])
                if match == "TRUE":
                    print(f"Tool found: {id}")
                    return tool
            return None

        summary = summarizer.summarize(task_description)
        tool_or_none = try_retrieve_tool(summary)
        tool = tool_or_none if tool_or_none else generate_new_tool(summary)

        command = invoker.generate_invocation(
            id=tool['id'],
            task=task_description,
            arguments=tool['arguments'],
            argument_types=tool['argument_types'],
            summary=summary,
            implementation=tool['implementation'],
            save_file_name=f"save_runs/invocation_{tool.get('id')}.py"
        )
        tool["env_variables"] =  list(map(str.strip, tool['env_variables'].split(","))) if tool['env_variables'] != "NONE" else []
        tool["dependencies"] = list(map(str.strip, tool['dependencies'].split(","))) if tool['dependencies'] != "NONE" else []
        print(tool['env_variables'])
        print(tool['dependencies'])
        tool['command'] = command
        return tool

        # return {
        #     "id": tool['id'],
        #     "command": command,
        #     "implementation": tool['implementation'],
        #     "env_variables": tool['env_variables'].split(",") if tool['env_variables'] != "NONE" else [],
        #     "dependencies": tool['dependencies'].split(",") if tool['dependencies'] != "NONE" else []
        # }

    def run_server(self):
        from flask import Flask, request, jsonify

        app = Flask(__name__)

        @app.route('/api/genTool', methods=['POST'])
        def gen_tool():
            data = request.get_json()

            if not data or 'task' not in data:
                return jsonify({'error': 'Missing task in request body'}), 400

            task = data['task']
            try:
                result = self.handle_tool_request(task)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        app.run(port=5000)

# take in a clear_db flag
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clear_db", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
