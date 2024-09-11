import requests
import json
import os

class UdioWrapper:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.api_url = "https://www.udio.com/api/generate-proxy"

    def create_complete_song(self, short_prompt, extend_prompts, outro_prompt, num_extensions, custom_lyrics_short, custom_lyrics_extend, custom_lyrics_outro):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        data = {
            "short_prompt": short_prompt,
            "extend_prompts": extend_prompts,
            "outro_prompt": outro_prompt,
            "num_extensions": num_extensions,
            "custom_lyrics_short": custom_lyrics_short,
            "custom_lyrics_extend": custom_lyrics_extend,
            "custom_lyrics_outro": custom_lyrics_outro
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.content  # Assuming the API returns the audio file directly
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Udio API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None
