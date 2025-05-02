from llm.go_cass_llm import GoCaas
from llm.token_manager import TokenManager
from typing import Optional, List
import json

reflect_propmt = """
## 🧠 Objective
You are a profession agent that help to reply to the user according to the server results and user request.

## 📝 Instructions
- You are given a server running result in JSON format.
- You are given a user initial objective in natural language.
- Generate a short message to summarize the results less than 50 words.

## Response Format
- Return a JSON object with the following keys:
    - "message": A string message to the user
    - "results": A list of JSON objects that passed to you from the server.
"""

def reply(objective: str, results: List) -> dict:
    """Reflect the feedback to the MCP client."""
    llm = GoCaas()
    token = TokenManager().token
    prompt = f"{reflect_propmt}\n\n## Objective\n{objective}\n\n## Results\n{results}"
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
    objective = "I want to know the value of the domain name exampledomain.com and other performance metrics."
    results =  [
    {
      "domain_evaluation_tool": {
        "Domain Name": "exampledomain.com",
        "Keyword & SEO Value": {
          "summary": "Contains high-value keywords, enhancing SEO potential. Moderate CPC value with competitive advantages in search.",
          "rating": 8.5
        },
        "SLD Structure & Length": {
          "summary": "Short, clear SLD with 12 characters. Memorable and minimizes potential typos.",
          "rating": 9
        },
        "Brandability & Positioning": {
          "summary": "Easy to pronounce and remember. Sounds premium and aligns with a wide market.",
          "rating": 8.7
        },
        "Trustworthiness & TLD": {
          "summary": ".com TLD is trusted globally with no malicious history. Secure HTTPS availability.",
          "rating": 9.2
        }
      }
    },
    {   
      "domain_govalue_tool": {
        "valuation_data": None,
      }
    }
  ]
    session_id = None
    resp = reflect(objective, results)
    print("resp", resp)