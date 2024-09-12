from .udio_authenticator import UdioAuthenticator
from .udio_song_generator import UdioSongGenerator

class UdioWrapper:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.song_generator = UdioSongGenerator(authenticator)

    def create_complete_song(self, *args, **kwargs):
        return self.song_generator.generate_song(*args, **kwargs)
