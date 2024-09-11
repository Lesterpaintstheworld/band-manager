import requests

class UdioWrapper:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.base_url = "https://api.udio.com/v1"

    def create_complete_song_stream(self, **kwargs):
        url = f"{self.base_url}/complete-song"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=kwargs, headers=headers, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=8192)
