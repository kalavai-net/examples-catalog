from pydub import AudioSegment
import os

def convert_webm_to_mp3(webm_filepath, mp3_filepath):
    """Converts a .webm file to .mp3."""
    if not os.path.exists(webm_filepath):
        raise FileNotFoundError(f"The file {webm_filepath} does not exist.")

    audio = AudioSegment.from_file(webm_filepath, format="webm")
    audio.export(mp3_filepath, format="mp3")

if __name__ == "__main__":
    convert_webm_to_mp3(
        webm_filepath="audio.webm",
        mp3_filepath="_audio.mp3"
    )
