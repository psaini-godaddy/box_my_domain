import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.mcp_prompts import format_prompt_from_s3
from llm.token_manager import TokenManager
from llm.go_caas_llm import GoCaas
import json

def metadata():
    return {
        "tool_id": "domain_evaluation_tool",
        "name": "Domain Name Evaluating Tool",
        "description": (
            "Evaluates domain names based on various criteria. Provides insights into domain value and potential."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"}
            },
            "required": ["domain_name"]
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                
                "Domain Name": {"summary": {"type": "string"}, "rating": {"type": "double"} },
                "Keyword & SEO Value": {"summary": {"type": "string"}, "rating": {"type": "double"} },
                "SLD Structure & Length": {"summary": {"type": "string"}, "rating": {"type": "double"} },
                "Brandability & Positioning": {"summary": {"type": "string"}, "rating": {"type": "double"} },
                "Trustworthiness & TLD": {"summary": {"type": "string"}, "rating": {"type": "double"} }
            }
        },
        "tags": ["github", "semgrep", "issues", "pull-requests", "branches"],
        "tool_type": "data_retrieval"
    }


def run(input_data, session_id: str, context: dict = None):
    """Run the Domain Evaluation Tool."""
    prompt_id = "domain-evaluation"

    # Format the prompt using the input data
    prompt = format_prompt_from_s3(prompt_id, {
        "domain_name": input_data.get("domain_name")
    })
    
    print(f"🧠 [Domain Evaluation Tool] LLM Prompt:\n{prompt}")

    # Call the LLM with the formatted prompt
    token = TokenManager().token
    llm = GoCaas()
    response = llm.call(token, prompt)

    try:
        cleaned = response.replace("```yaml", "").replace("```", "").strip()
        print(f"📜 Cleaned LLM Response:\n{cleaned}")
        
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"❌ Failed to parse LLM response: {e}\nRaw response:\n{response}")




def main():
    """Main function to test the Domain Evaluation Tool."""
    # Example input data
    input_data = {
        "domain_name": "ericbikeshop.com"
    }

    print("🔍 Running Domain Evaluation Tool...")
    try:
        # Run the tool and capture the output
        output = run(input_data, "", {})
        print("✅ Tool Output:")
        print(type(output))
        print(json.dumps(output, indent=4))
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()