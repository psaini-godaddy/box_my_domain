from llm.go_cass_llm import GoCaas
from llm.token_manager import TokenManager
import json

reflect_propmt = """
## 🧠 Objective
You are a tool reflection agent. Your job is to reflect the feedback and decide which actions should be removed from current action dictionaries.

## Response Format
- Return a JSON object with the following keys:
  - `actions`: A list of action IDs to be removed from the current action dictionaries.
"""

def reflect(feedback: str, actions: dict) -> dict:
    """Reflect the feedback to the MCP client."""
    llm = GoCaas()
    token = TokenManager().token
    prompt = f"{reflect_propmt}\n\n## Feedback\n{feedback}\n\n## Actions\n{actions}"
    prompt = f"{reflect_propmt}\n\n## Feedback\n{feedback}\n\n## Actions\n{actions}"
    response = llm.call(token, prompt)
    response = response.replace("```json", "")
    response = response.replace("```", "")  # Remove any code block markers
    response = response.strip()
    try:
        print("[GoCaas] 🧠 Parsing LLM response...")
        response = response.replace("```json", "")
        response = response.replace("```", "")  # Remove any code block markers
        parsed = json.loads(response.strip())
        return parsed
    except Exception as e:
        print(f"[GoCaas] ❌ Failed to parse LLM output: {e}")
        print("LLM raw output:", response)
        return
    
    

if __name__ == "__main__":
    feedback = "I only want to use Valuation API"
    actions = {'act-001': {'action_id': 'act-001', 'name': 'Evaluate Domain Name', 'description': 'Evaluate the domain name google.com to provide insights into its value and potential.', 'metadata': {'tool': 'domain_evaluation_tool', 'params': {'domain_name': 'google.com'}}}, 'act-002': {'action_id': 'act-002', 'name': 'Fetch Domain Valuation Data', 'description': 'Fetch and parse domain valuation data for google.com from the valuation API.', 'metadata': {'tool': 'domain_govalue_tool', 'params': {'domain_name': 'google.com'}}}}
    session_id = None
    resp = reflect(feedback, actions)
    print("resp", resp)