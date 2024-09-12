import requests
import logging
import tempfile
import os
import time
import random

class SunoSongGenerator:
    API_BASE_URL = "https://api.suno.ai"

    def __init__(self, suno_cookie):
        self.suno_cookie = suno_cookie
        self.logger = logging.getLogger(__name__)

    def generate_song(self, prompt, make_instrumental=False, wait_audio=False):
        try:
            self.logger.info(f"Generating song with prompt: {prompt}")
            
            payload = {
                "prompt": prompt,
                "make_instrumental": make_instrumental,
                "wait_audio": wait_audio
            }
            headers = {'Cookie': self.suno_cookie}
            
            response = requests.post(f"{self.API_BASE_URL}/api/generate", json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Suno API response: {data}")
            
            if not isinstance(data, list) or len(data) < 2:
                raise ValueError("Unexpected response format from Suno API")
            
            return data[0]['id'], data[1]['id']
        except Exception as e:
            self.logger.error(f"Failed to generate song: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate song: {str(e)}")

    def get_audio_urls(self, ids, max_attempts=60, delay=5):
        try:
            ids_str = f"{ids[0]},{ids[1]}"
            for _ in range(max_attempts):
                response = requests.get(f"{self.API_BASE_URL}/api/get?ids={ids_str}", headers={'Cookie': self.suno_cookie})
                response.raise_for_status()
                audio_info = response.json()
                
                if all(info['status'] == 'streaming' for info in audio_info):
                    return [info['audio_url'] for info in audio_info if 'audio_url' in info]
                
                time.sleep(delay)
            
            raise Exception("Timeout: Audio generation took too long or no audio URLs were provided.")
        except Exception as e:
            self.logger.error(f"Failed to get audio URLs: {str(e)}", exc_info=True)
            raise Exception(f"Failed to get audio URLs: {str(e)}")

    def create_complete_song(self, prompt, make_instrumental=False):
        try:
            # Generate initial song
            ids = self.generate_song(prompt, make_instrumental)
            
            # Get audio URLs
            audio_urls = self.get_audio_urls(ids)
            
            # Download and save the audio files
            song_paths = []
            for i, url in enumerate(audio_urls):
                song_filename = f"song_{int(time.time())}_{i}.mp3"
                song_path = os.path.join("songs", song_filename)
                os.makedirs("songs", exist_ok=True)
                
                response = requests.get(url)
                response.raise_for_status()
                
                with open(song_path, 'wb') as f:
                    f.write(response.content)
                self.logger.info(f"Song part {i+1} saved successfully at: {song_path}")
                song_paths.append(song_path)
            
            self.logger.info("Complete song sequence generated successfully")
            return song_paths
        except Exception as e:
            self.logger.error(f"Failed to create complete song: {str(e)}")
            raise Exception(f"Failed to create complete song: {str(e)}")
