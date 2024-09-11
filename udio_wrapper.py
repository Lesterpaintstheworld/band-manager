from udio_wrapper import UdioWrapper as UdioWrapperBase

class UdioWrapper(UdioWrapperBase):
    def create_complete_song(self, short_prompt, extend_prompts, outro_prompt, num_extensions, custom_lyrics_short, custom_lyrics_extend, custom_lyrics_outro):
        try:
            song_sequence = self.create_song(
                prompt=short_prompt,
                custom_lyrics=custom_lyrics_short
            )
            
            for i in range(num_extensions):
                song_sequence = self.extend(
                    prompt=extend_prompts[i],
                    audio_conditioning_path=song_sequence,
                    audio_conditioning_song_id=song_sequence.split('/')[-1].split('.')[0],
                    custom_lyrics=custom_lyrics_extend[i]
                )
            
            song_sequence = self.add_outro(
                prompt=outro_prompt,
                audio_conditioning_path=song_sequence,
                audio_conditioning_song_id=song_sequence.split('/')[-1].split('.')[0],
                custom_lyrics=custom_lyrics_outro
            )
            
            return song_sequence
        except Exception as e:
            print(f"Error creating complete song with Udio: {e}")
            return None
