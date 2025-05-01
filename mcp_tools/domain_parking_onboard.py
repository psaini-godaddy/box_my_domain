def metadata():
    return {
        "tool_id": "domain_parking_onboard",
        "name": "Domain Name Onboard helper",
        "description": (
            "Parking onboard tool is a tool that helps users to put their domain starts to show ads. Users can earn money from their domain names by showing ads on their parked domains based on the traffic. It suits for users who want to earn money from their domain names without selling them."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "shopper_id": {"type": "string"},
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
        "tags": ["parking", "ads", "api", "domain", "profit"],
        "tool_type": "product_registration"
    }
    
def run(input_data, session_id: str, context: dict = None):
    domain_name = input_data.get("domain_name")
    shopper_id = input_data.get("shopper_id")
    return {
        "message": f"Congratulations! Your domain name '{domain_name}' has been parked successfully.",
    }
    
if __name__ == "__main__":
    resp = run({'domain_name': 'example.com', 'shopper_id': '12345'}, "session_id")
    print(resp)