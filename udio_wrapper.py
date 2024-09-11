import udio

class UdioWrapper:
    def __init__(self, auth_token):
        self.udio = udio.Udio(auth_token)

    def create_complete_song(self, short_prompt, extend_prompts, outro_prompt, num_extensions, custom_lyrics_short, custom_lyrics_extend, custom_lyrics_outro):
        try:
            song = self.udio.create_complete_song(
                short_prompt=short_prompt,
                extend_prompts=extend_prompts,
                outro_prompt=outro_prompt,
                num_extensions=num_extensions,
                custom_lyrics_short=custom_lyrics_short,
                custom_lyrics_extend=custom_lyrics_extend,
                custom_lyrics_outro=custom_lyrics_outro
            )
            return song.audio_data  # Assuming this returns the audio data
        except Exception as e:
            print(f"Error creating complete song with Udio: {e}")
            return None
