class UdioAuthenticator:
    API_BASE_URL = "https://www.udio.com/api"

    def __init__(self, auth_token1, auth_token2):
        self.auth_token1 = auth_token1
        self.auth_token2 = auth_token2

    def get_headers(self, get_request=False):
        headers = {
            "Accept": "application/json, text/plain, */*" if get_request else "application/json",
            "Content-Type": "application/json",
            "Cookie": f"; sb-ssr-production-auth-token.0={self.auth_token1}; sb-ssr-production-auth-token.1={self.auth_token2}",
            "Origin": "https://www.udio.com"
        }
        return headers

    def test_connection(self):
        # Implement logic to test the connection to the Udio API
        pass
