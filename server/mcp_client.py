import requests
import json

class MCPClient:
    def __init__(self, rpc_server: str):
        self.rpc_server = rpc_server
        session_id, token = self._start_session()
        self.session_id = session_id
        self.token = token
        self.is_interactive = False
        self.is_executing = False
    def _start_session(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "mcp.startSession",
            "params": {},
            "id": "session-start"
        }
        response = requests.post(self.rpc_server, json=payload)
        response.raise_for_status()

        data = response.json()
        if "result" not in data:
            raise Exception(f"Failed to start session: {data}")
        session_id = data["result"].get("session_id")
        token = data["result"].get("access_token")

        print(f"✅ Session started\n  Session ID: {session_id}\n  Access Token: {token[:20]}...")

        return session_id, token
    
    def call(self, method: str, params: dict):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "cli-request"
        }
        headers = {"Authorization": f"Bearer {self.token}", "session_id": self.session_id}
        response = requests.post(self.rpc_server, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    filtered_tools = 'user_interaction'
    RPC_URL = "https://dridata-mcp-server-dev-private.dridata-dev-private.prod.onkatana.net/rpc"
    client = MCPClient(RPC_URL)
    
    # response= client.call("tools/list", {})
    # for tool in response['result']:
    #     print("==============")
    #     print(tool)
    #     print("==============")
    
    # domain = "example.com"
    # response = client.call("mcp.getSessionInfo", {})
    # objective = f"Use govalue_tool. Envaluate domain {domain}'s price and other performance metrics "
    # print(objective)
    # response = client.call("plan/generate", {"objective": objective})
    # print(response.get("result").get("plan", []))
    # plans = response.get("result", {}).get("plan", [])
    # for plan in plans.get("actions", []):
    #     print(plan)
    # response = client.call('tools/call', {
    #         "tool_id": 'domain_aftermarket_onboard',
    #         "parameters": {"domain_name":"hellofresh.com"},
    # })
    # print("response", response)
    
    
    response = client.call('tools/register', {})
    print("response", response)
    #     print(response)
    
    # resposne = client.call("plan/generate", {"objective": "I want to evaluate domain_name 'hellofresh.com' by domain price. Do not use user_interaction tool"})
    
    # print(resposne)
    # print("reflect first ==============")
    # client.call('reflect/first', {})
    
    # actions = {}
    # for action in resposne['result']['plan']['actions']:
    #     actions[action['action_id']] = action['metadata']
    # print("actions", actions)
    # response = client.call('reflect/first', {})
    # last_action_id = response['result']['next_action_id']
    # print("action_id", last_action_id)
    # del actions[last_action_id]
    # while actions:
    #     response = client.call('reflect/next', {'last_action_id': last_action_id})
    #     last_action_id = response['result']['next_action_id']
    #     if not last_action_id:
    #         break
    #     print("action_id", last_action_id)
    #     del actions[last_action_id]
    
    