
class TokenManager:
    def __init__(
        self,
        sso_host="sso.dev-godaddy.com",
        refresh_min_interval=45,
        primary_region="us-west-2",
        secondary_region="us-west-2"
    ):
        from gd_auth.client import AwsIamAuthTokenClient

        self.sso_client = AwsIamAuthTokenClient(
            sso_host,
            refresh_min=refresh_min_interval,
            primary_region=primary_region,
            secondary_region=secondary_region
        )

        # Auto-refresh token on initialization
        self._token = self.sso_client.token

    @property
    def token(self) -> str:
        return self._token
