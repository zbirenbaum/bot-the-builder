from btb import ToolAgentClient
from dotenv import load_dotenv
load_dotenv()

client = ToolAgentClient()
res = client.give_task('use alphavantage api to aapl daily price data from jan 1st to jan 15 2024')
print(res)
# res = client.give_task("add 10 and 7")['result']
# print(res)
# print(client.give_task(f"add {res} and 7"))
