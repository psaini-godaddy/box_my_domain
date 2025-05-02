from fastapi import FastAPI
from mcp_client import MCPClient

from typing import Optional, List
from pydantic import BaseModel, Field   # Field is optional, but handy for docs
from reflector import reflect
from reply_client import reply
import requests

class RequestBody(BaseModel):
    message:    Optional[str] = None
    session_id: Optional[str] = None
    
class ResponseBody(BaseModel):
    status: str
    error: Optional[str] = None
    result: Optional[List] = None    
    session_id: str

RPC_URL = "https://dridata-mcp-server-dev-private.dridata-dev-private.prod.onkatana.net/rpc"

app = FastAPI(title="FastAPI Sample", version="1.0.0")
mcp_client ={}

mcp_actions = {}
mcp_messages = {}

aftermarket_token = """
"""

def get_mcp_client(session_id: str = None) -> MCPClient:
    """Get MCP client instance."""
    if not session_id:
        client = MCPClient(RPC_URL)
        mcp_client[client.session_id] = client
    else:
        client = mcp_client.get(session_id)
        if not client:
            raise ValueError(f"Session ID {session_id} not found.")
    return client

@app.get("/health")
async def health() -> dict[str, str]:
    """Health‑check endpoint."""
    return {"status": "ok"}


def mcp_plan(body: RequestBody) -> ResponseBody:
    """Accepts the specified JSON payload and echoes it back."""
    session_id = body.session_id
    if not session_id:
        client = get_mcp_client()
        session_id = client.session_id
        mcp_messages[session_id] = body.message
        message = mcp_messages[session_id] + 'do not use user_interaction tool'
        response = client.call("plan/generate", {"objective": message})
        actions = {}
        for action in response['result']['plan']['actions']:
            actions[action['action_id']] = action
        mcp_actions[session_id] = actions
        response = client.call("plan/explain", {})
        if response.get("error"):
            return ResponseBody(status="error", error=response["error"])
        else:
            return ResponseBody(status="ok", result=[response["result"]], session_id=session_id)
    else:
        client = get_mcp_client(session_id)
        actions = mcp_actions.get(session_id)
        mcp_messages[session_id] += '\n' + body.message
        skip_action_ids = reflect(mcp_messages[session_id], actions)
        print("skip_action_ids", skip_action_ids)
        if not skip_action_ids:
            return ResponseBody(status="error", error="No actions found to skip.")
        response = client.call("plan/update", {"feedback": skip_action_ids})
        response = client.call("plan/generate", {"objective": mcp_messages[session_id]})
        actions = {}
        for action in response['result']['plan']['actions']:
            actions[action['action_id']] = action
        mcp_actions[session_id] = actions
        response = client.call("plan/explain", {"session_id": session_id})
        if response.get("error"):
            return ResponseBody(status="error", error=response["error"])
        else:
            return ResponseBody(status="ok", result=[response["result"]], session_id=session_id)

def mcp_execute(session_id: str, message: str = None) -> ResponseBody:
    """Accepts the specified JSON payload and echoes it back."""
    client = get_mcp_client(session_id)
    client.is_executing = True
    actions = mcp_actions.get(session_id)
    response = client.call('reflect/first', {})
    action_id = response['result']['next_action_id']
    if not actions:
        return ResponseBody(status="error", error="No actions found for the given session ID.")
    
    # if not client.is_interactive and action['metadata']['tool'] == 'user_interaction':
    #     client.is_interactive = True
    #     print(action['metadata']['params']['user_message'])
    #     result = [{"user_message": action['metadata']['params']['user_message']}]
    #     print("result=====>", result)
    #     print(ResponseBody(status="ok", 
    #                         result=[{"user_message": action['metadata']['params']['user_message']}], 
    #                         session_id=client.session_id))
    #     return ResponseBody(status="ok", 
    #                         result=[{"user_message": action['metadata']['params']['user_message']}], 
    #                         session_id=client.session_id)
    
    # if client.is_interactive:
    #     response = client.call("tools/call", {
    #         "tool_id": action['metadata']["tool"], 
    #         "parameters": {"interaction_type": action['metadata']["params"]["interaction_type"],
    #                        "user_message": message,
    #                        "context": action['metadata']['params']["context"]}})
        
    #     print("response=====>", response)
    #     client.is_interactive = False
    
    print("actions", actions)
    action = actions[action_id]
    results = []
    response = client.call('tools/call', {
        "tool_id": action['metadata']["tool"],
        "parameters": action['metadata']["params"],
    })
    print("response=====>", response)
    del actions[action_id]
    print(actions)
    results.append(response['result'])
    while actions:
        response = client.call('reflect/next', {'last_action_id': action_id})
        print("response reflect/next=====>", response)
        action_id = response['result']['next_action_id']
        if not action_id:
            break
        print("action_id", action_id)
        results.append(client.call('tools/call', {
            "tool_id": actions[action_id]['metadata']["tool"],
            "parameters": actions[action_id]['metadata']["params"],
        }))
        del actions[action_id]
    client.is_executing = False
    return ResponseBody(status="ok", result=results, session_id=session_id)



@app.post("/mcp/chat")
async def mcp_chat(body: RequestBody) -> ResponseBody:
    session_id = body.session_id
    if not session_id:
        print("planning")
        response = mcp_plan(RequestBody(message=body.message, session_id=session_id))
        return response
    else:
        client = get_mcp_client(session_id)
        if 'yes' in body.message.lower() or client.is_executing:
            print("executing")
            return mcp_execute(session_id)
        else:
            print("planning")
            return mcp_plan(RequestBody(message=body.message, session_id=session_id))


@app.post("/mcp/plan_excute")
async def mcp_plan_execute(body: RequestBody) -> ResponseBody:
    """Accepts the specified JSON payload and echoes it back."""
    client = get_mcp_client()
    session_id = client.session_id
    message = body.message
    message += 'do not use user_interaction tool, and only extract information from objective'
    response = client.call("plan/generate", {"objective": message})
    print("Plan Genrate response=====>\n", response)
    if response.get("error"):
        return ResponseBody(status="error", error=response["error"])
    else:
        results = []
        
        for tool in response['result']['plan']['actions']:
            print("tools=====>", tool)
            if tool['metadata']['tool'] == 'domain_aftermarket_onboard':
                print("domain_aftermarket_onboard")
                tool['metadata']["params"].update({"AUTH_IDP": aftermarket_token})
                response = client.call('tools/call', {
                    "tool_id": tool['metadata']["tool"],
                    "parameters": tool['metadata']["params"],
                })
            else:
                response = client.call('tools/call', {
                        "tool_id": tool['metadata']["tool"],
                        "parameters": tool['metadata']["params"],
                })
                print("response=====>", response)
            results.append(
                {tool['metadata']["tool"]: response['result']['output']})
        final_response = reply(message, results)
        print("final_response=====>", final_response)
        return ResponseBody(status="ok", result=results, session_id=session_id)

@app.get("/get_domain_go_value")
def get_domain_go_value(domain: str, session_id: str = None) -> ResponseBody:
    """Get domain value from the external API."""
    client = get_mcp_client(session_id)
    session_id = client.session_id
    objective = f"I want to know the value of the domain name {domain} and other performance metrics. Do not use user_interaction tool."
    print("panning -- objective=====>", objective)
    response = client.call("plan/generate", {"objective": objective})
    plans = response.get("result", {}).get("plan", [])
    result = []
    for plan in plans.get("actions", []):
        print('plan=====>', plan)
        response = client.call('tools/call', {
                "tool_id": plan.get('metadata').get("tool"),
                "parameters": plan.get('metadata').get("params"),
        })
        print('response=====>', response)
        result.append(response['result']['output'])

    return {
        "status": "ok",
        "result": result,
        "session_id": session_id
    }

@app.get("/domain_draw")
async def domain_draw(price : float, search_query : str = None) -> ResponseBody:
    client = get_mcp_client()
    session_id = client.session_id
    if search_query:
        url = f'http://vectordb.cloud.phx3.gdg:8005/v1/mystery_box_rec?price={price}&search_query={search_query}&session_id={session_id}'
    else:
        url = f'http://vectordb.cloud.phx3.gdg:8005/v1/mystery_box_rec?price={price}&session_id={session_id}'
    response = requests.get(url)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        return ResponseBody(status="ok", result=[data], session_id=session_id)
    else:
        return ResponseBody(status="error", error="Failed to fetch data from the external API")
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
