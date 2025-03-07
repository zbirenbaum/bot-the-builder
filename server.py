from btb import ToolAgentServer
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    server = ToolAgentServer(True)
    server.run_server()
