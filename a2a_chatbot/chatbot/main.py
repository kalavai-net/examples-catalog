import sounddevice as sd
import soundfile as sf
import io
import openai
import re
import httpx


# Set OpenAI-compatible API base URL (change if hosted remotely)
LLM_API_URL = "http://192.168.68.58:31110/v1"  # Change to your vLLM server URL
LLM_API_KEY = "sk-1234"  # Not needed for vLLM, but required by openai lib
LLM_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
TTS_API_URL = "http://192.168.68.58:32531"
AUDIO_SPEED = 1.1

client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_URL)

# Function to synthesize and play speech in real-time
def speak_text(text_chunk):
    client = httpx.Client(base_url=TTS_API_URL)
    response = client.post(
        "/v1/audio/speech",
        json={
            "input": text_chunk,
            "model": "hexgrad/Kokoro-82M",
            "response_format": "wav",
            "speed": AUDIO_SPEED
        },
        timeout=60
    )
    wav_bytes = response.read()
    wav_io = io.BytesIO(wav_bytes)
    try:
        data, samplerate = sf.read(wav_io, dtype='float32')
        # Play the audio
        sd.play(data, samplerate=22000)
        sd.wait()
    except:
        pass

def generate_response(prompt):
    """Streams response from vLLM OpenAI-compatible API, yielding full sentences."""

    response = client.chat.completions.create(
        model=LLM_MODEL_ID,  # Must match the served model
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        stream=True,  # Enables token-by-token streaming
    )

    buffer = ""
    sentence_endings = re.compile(r'([.!?])\s')

    for chunk in response:
        token = chunk.choices[0].delta.content or ""
        buffer += token

        # Check if we have a full sentence
        match = sentence_endings.search(buffer)
        if match:
            sentence, buffer = buffer[:match.end()], buffer[match.end():]
            yield sentence.strip()

    # Yield any remaining text after streaming ends
    if buffer.strip():
        yield buffer.strip()

def chat_with_voice():
    while True:
        user_input = input("You: ")
        print("Bot: ", end="", flush=True)

        tokens = []
        try:
            for token in generate_response(user_input):  # Stream LLM output
                tokens.append(token)
                print(token, end="", flush=True)
                speak_text(token)  # Convert token to speech in real-time
        except KeyboardInterrupt:
            pass
        print("\n")  # New line after response

# Run the chatbot
chat_with_voice()

# for token in generate_response("what?"):
#     print(token, end="", flush=True)
# print()
#speak_text("What is the square root of pi? Good question, let me go and find out. First things first, I do not know how to calculate it, but I have a buddy that can!")
