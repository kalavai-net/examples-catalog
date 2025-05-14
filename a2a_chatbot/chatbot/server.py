# server.py
import argparse
import base64

import torch
import io
from TTS.api import TTS
import litserve as ls
import soundfile as sf


# (STEP 1) - DEFINE THE API (compound AI system)
class SimpleLitAPI(ls.LitAPI):

    def __init__(self, model_name="tts_models/en/vctk/vits", speaker="p364"):
        self.model_name = model_name
        self.speaker = speaker

    def setup(self, device):
        # setup is called once at startup. Build a compound AI system (1+ models), connect DBs, load data, etc...
        self.model = TTS(self.model_name).to(device) 

    def decode_request(self, request):
        # Convert the request payload to model input.
        return request["input"] 

    def predict(self, text_chunk):
        wav = self.model.tts(text=text_chunk, speaker=self.speaker)
        if isinstance(wav, torch.Tensor):
            wav = wav.numpy()

        # Write the numpy array to an in-memory buffer in WAV format
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, wav, samplerate=22050, format='WAV')
        audio_buffer.seek(0)
        audio_data = audio_buffer.getvalue()
        audio_buffer.close()

        return {"output": audio_data}

    def encode_response(self, prediction):
        # Convert the model output to a response payload.
        audio_content_base64 = base64.b64encode(prediction["output"]).decode("utf-8")
        return {"audio_content": audio_content_base64, "content_type": "audio/wav"}


# (STEP 2) - START THE SERVER
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--max_batch_size", default=1, type=int)
    parser.add_argument("--accelerator", default="cpu", type=str)

    args = parser.parse_args()
    server = ls.LitServer(
        SimpleLitAPI(),
        accelerator=args.accelerator,
        max_batch_size=args.max_batch_size)
    server.run(port=args.port, num_api_servers=1)
