import requests

def metadata():
    return {
        "tool_id": "domain_aftermarket_onboard",
        "name": "Domain Name Onboard helper",
        "description": (
            "Aftermarket onboard tool is a tool that helps users to put their domain names on the aftermarket. It will help users to resell their domain names for more profit."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain_name": {"type": "string"},
                "buynow_price": {"type": "double"},
                "floor_price": {"type": "double"},
                "leasing_enabled": {"type": "boolean"},
                "maxLease_period": {"type": "integer"},
                "minbid_price": {"type": "double"}
            },
            "required": ["domain_name", "buynow_price", "floor_price"],
        },
        "outputSchema": {
            "type": "object",
            "message": {
                "type": "string",
                "description": "Message indicating the success of the onboarding process."
            },
            "response": {
                "type": "object",
                "description": "Response from the API after listing the domain."
            }
        },
        "tags": ["aftermarket", "sell", "api", "profit", "domain"],
        "tool_type": "product_registration"
    }
    
def run(input_data, session_id: str, context: dict = None):
    domain_name = input_data.get("domain_name")
    buynow_price  = input_data.get("buynow_price", 1000)
    floor_price = input_data.get("floor_price", 100)
    leasing_enabled = input_data.get("leasing_enabled", False)
    max_lease_period = input_data.get("maxLease_period", 36)
    min_bid_price = input_data.get("minbid_price", 20)
    auth_idp = input_data.get("AUTH_IDP").strip()
    
    URL = "https://am-ui-services.api.int.dev-afternic.com/v1/customers/my/domains"

    AUTH_IDP = auth_idp          # export AUTH_IDP="eyJhbGciOiJ..."
    if not AUTH_IDP:
        raise RuntimeError("Set the AUTH_IDP env var with your SSO JWT")

    HEADERS = {
        "Authorization": f"sso-jwt {AUTH_IDP}",
        "Content-Type": "application/json",
    }

    
    PAYLOAD = {
        "backgroundColorCustom": "#ABCDEF",
        "backgroundColorOption": "CORAL_GRADIENT",
        "buynowPrice": int(buynow_price * 10e6),
        "domain": domain_name,
        "floorPrice": int(floor_price * 10e6),
        "fontColorOption": "DARK",
        "hidden": False,
        "landingPage": "SALES_TYPE",
        "intakeStyle": "PRICE_FORM",
        "leasingEnabled": leasing_enabled,
        "maxLeasePeriod": max_lease_period,
        "minbidPrice": int(min_bid_price * 10e6),
        "transferOption": 1,
    }
    resp = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=10)
    
    return {
        "message": f"Congratulations! Your domain name '{domain_name}' has been successfully listed to the aftermarket. Please log on to afternic.com to manage your domain name.",
        "response": resp.json(),
    }
    
if __name__ == "__main__":
    aftermarket_token = """
"""
    print(run(
        {'domain_name': 'example7423511.com', 
         'buynow_price': 1000, 
         'floor_price': 100,
         'AUTH_IDP': aftermarket_token,},
        "session_id"))