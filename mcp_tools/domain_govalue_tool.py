# query_tool.py — MCP-Compliant Athena CTAS Generator using LLM (GoCaaS)

import json
import requests
import sys
import os
import boto3

# Add the parent directory to the Python path to resolve the ModuleNotFoundError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from llm.token_manager import TokenManager
from llm.go_caas_llm import GoCaas
from server.mcp_prompts import format_prompt_from_s3

DEFAULT_REGION = "us-west-2"
ATHENA_DB = "default"


def metadata():
    return {
        "tool_id": "domain_govalue_tool",
        "name": "Domain Valuation Tool",
        "description": (
            "Fetches and parses domain valuation data from the valuation API. "
            "Returns detailed pricing, trends, and other domain-related information."
        ),
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
                "valuation_data": {"type": "object"}
            }
        },
        "tags": ["domain", "valuation", "pricing", "trends"],
        "tool_type": "data_retrieval"
    }



def run(parameters: dict, session_id: str = None, context: dict = None):
    """
    Executes the domain valuation tool based on the provided input data.

    Args:
        input_data (dict): Input data containing the domain name.

    Returns:
        dict: Output data containing the valuation data.
    """
    
    domain_name = parameters.get("domain_name")
    if not domain_name:
        raise ValueError("Input data must contain 'domain_name'.")

    valuation_data = fetch_domain_valuation(domain_name)
    print(valuation_data.keys())
    results = {}
    results["domain_name"] = domain_name
    results["prices"] = valuation_data.get("prices")
    if valuation_data:
        return {"valuation_data": results}
    else:
        return {"valuation_data": None}


def main():
    """
    Main function to test the domain valuation tool interactively.
    """
    input_data = {
        "domain_name": "abc.io"
    }
    print(input_data)
    try:
        output_data = run(input_data)
        print("\nDomain Valuation Data:")
        print(json.dumps(output_data, indent=4))
    except Exception as e:
        print(f"\nError: {e}")


def get_api_key():
    """
    Fetches the API key from AWS Secrets Manager.

    Returns:
        str: The API key.
    """
    secret_name = "/Team/Custom/Valuation/APIKey"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return get_secret_value_response["SecretString"]
    except Exception as e:
        print(f"❌ Failed to retrieve secret: {e}")
        return None


def fetch_domain_valuation(domain_name):
    """
    Fetches the domain valuation from the API and parses the result into a dictionary.

    Args:
        domain_name (str): The domain name to fetch the valuation for.

    Returns:
        dict: Parsed response from the API.
    """
    url = f"https://valuation.int.dev.gdcorp.tools/v6/appraisal/{domain_name}"
    api_key = get_api_key()
    if not api_key:
        print("❌ API key is missing. Cannot proceed with the request.")
        return None

    headers = {
        "Authorization": f"{api_key}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch domain valuation for {domain_name}: {e}")
        return None


if __name__ == "__main__":
    main()
