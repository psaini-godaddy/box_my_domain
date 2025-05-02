import os
from dotenv import load_dotenv
load_dotenv()

AWS_ENV = os.getenv("ENV", "dev")


def get_token_client(
    env=AWS_ENV, refresh_min_interval=45, primary_region="us-west-2", secondary_region="us-west-2"
):
    """
    Get the token from the AwsIamAuthTokenClient
    """
    from gd_auth.client import AwsIamAuthTokenClient

    if env == "prod":
        sso_host = "sso.godaddy.com"
    elif env == "test" or env == "ote":
        sso_host = "sso.test-godaddy.com"
    else:
        sso_host = "sso.dev-godaddy.com"

    return AwsIamAuthTokenClient(
        sso_host,
        refresh_min=refresh_min_interval,
        primary_region=primary_region,
        secondary_region=secondary_region,
    )

TOKEN = get_token_client()
token=TOKEN.token
# print(token)

with open(".jwt", "w") as f:
    f.write(token)

print("jwt_token saved to .jwt")