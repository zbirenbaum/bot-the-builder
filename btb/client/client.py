import requests
import os
import subprocess
from dotenv import load_dotenv
from typing import List
load_dotenv()

def run_command(id: str, command: str, implementation: str, env_variables: List[str], dependencies: List[str]):
    if env_variables:
        for var in env_variables:
            if os.getenv(var) is None:
                print(f"ERROR: Required environment variable {var} not found")
                return None

    if dependencies:
        # install all dependencies through pip
        subprocess.check_call(["uv", "pip", "install", *dependencies])

    # Create a temporary file named {id}.py
    temp_file_name = f"{id}.py"
    with open(temp_file_name, 'w') as f:
        f.write(implementation)
    out = None
    err = None

    try:
        # Run the command with environment variables inherited
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ,
            universal_newlines=True
        )
        out, err = process.communicate()

    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        # else:
        #     print("Output: \n{}\n".format(output))

    # finally:
    #     # Delete the temporary file
    #     if os.path.exists(temp_file_name):
    #         os.remove(temp_file_name)

    def decode_bytes(byte_str: str):
        if isinstance(byte_str, bytes):
            return byte_str.decode('utf-8')
        return byte_str
    return [
        eval(decode_bytes(out)) if out else None,
        eval(decode_bytes(err)) if err else None]


def request_tool(task: str):
    response = requests.post('http://localhost:5000/api/genTool', json={'task': task})
    return response.json()

class ToolAgentClient():
    def __init__(self):
        pass

    def give_task(self, task: str):
        tool = request_tool(task)
        (out, err) = run_command(tool['id'], tool['command'], tool['implementation'], tool['env_variables'], tool['dependencies'])
        if err:
            return {
                'status': 'ERROR',
                'result': err
            }
        else:
            return {
                'status': 'SUCCESS',
                'result': out
            }
