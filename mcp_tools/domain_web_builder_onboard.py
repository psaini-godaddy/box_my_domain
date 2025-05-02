def metadata():
    return {
        "tool_id": "domain_web_builder_onboard",
        "name": "Domain Name Onboard helper",
        "description": (
            "Web Builder onboard tool is a tool that helps users to put their domain names on the web. It will help users to build their own website with their domain names."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "shopper_id": {"type": "string"}
            },
            "required": ["domain_name"]
        },
        "outputSchema": {
            "type": "object",
            "message": {
                "type": "string",
                "description": "Message indicating the success of the onboarding process."
            }
        },
        "tags": ["web", "builder", "api", "domain", "Airo", "website", "create", "build"],
        "tool_type": "product_registration"
    }
    
def run(input_data, session_id: str, context: dict = None):
    domain_name = input_data.get("domain_name")
    shopper_id = input_data.get("shopper_id")
    price = input_data.get("price")
    return {
        "message": f"you can build your own website with your domain name '{domain_name}' using GoDaddy Web Builder. You can start building your website by clicking the link below.",
        "url": f"https://www.godaddy.com/en-ca/websites/website-builder",
    }
    
if __name__ == "__main__":
    resp = run({'domain_name': 'example.com', 'shopper_id': '12345', 'price': 35.00}, "session_id")
    print(resp)