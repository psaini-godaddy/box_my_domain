from mcp_client import MCPClient



client = MCPClient("https://dridata-mcp-server-dev-private.dridata-dev-private.prod.onkatana.net/rpc")

resposne = client.call("tools/register", {})
print(resposne['result'])
resposne = client.call("tools/list", {})
for tool in resposne['result']:
    print(tool['tool_id'])
    
response = client.call("tools/call", {"tool_id": "domain_govalue_tool", "parameters": {"domain_name": "hellofresh.com"}})
print(response)