"""Check this for async https://github.com/Chainlit/cookbook/blob/main/realtime-assistant/app.py"""
import io
import time
import httpx
import re
import asyncio
import string

import numpy as np
import chainlit as cl
from openai import AsyncOpenAI
import audioop
import wave


COGENAI_URL = "https://api.cogenai.kalavai.net/v1"
COGENAI_API_KEY = "sk-Sewi-UGdpPaihexBlXzTkA"  # Not needed for vLLM, but required by openai lib
LLM_MODEL_ID = "qwen-qwen3-30b-a3b"
TTS_MODEL_ID = "hexgrad-kokoro-82m"
TTS_VOICE = "af" #"bm_lewis" # "af"
AUDIO_SPEED = 1.25
TEXT_SPEED = 0.05 # less is faster
SEGMENT_CHUNK_SIZE = 500 # max number of characters per audio/video segment
# Define a threshold for detecting silence and a timeout for ending a turn
SILENCE_THRESHOLD = 2500 # Adjust based on your audio level (e.g., lower for quieter audio)
SILENCE_TIMEOUT = 1500.0 # Seconds of silence to consider the turn finished


llm_client = AsyncOpenAI(api_key=COGENAI_API_KEY, base_url=COGENAI_URL)



##### UTILS ########
def clean_text_for_audio(text):
    acceptable_chars = string.ascii_letters + string.digits + string.punctuation + ' '
    return "".join(c for c in text if c in acceptable_chars)

def split_text(text, max_length=SEGMENT_CHUNK_SIZE):
    chunks = []
    current_chunk = ""
    sentences = re.split('([.!?]+)', text)  # Split keeping the punctuation
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def generate_audio(text, mime_type="wav", audio_speed=1.0):
    # Split text into chunks of 400 characters, trying to break at sentence endings
    # this is required since speaches models has a limit of 10-30 seconds audio
    cleaned_text = clean_text_for_audio(text)
    text_chunks = split_text(cleaned_text)
    print(f"--> Generating audio for {len(text_chunks)} chunks")
    t = time.time()
    
    all_audio_chunks = []
    total_duration = 0

    client = httpx.Client(base_url=COGENAI_URL)
    
    for chunk_idx, text_chunk in enumerate(text_chunks):
        try:
            print(f"Processing chunk {chunk_idx + 1}/{len(text_chunks)}: {text_chunk[:50]}...")
            response = client.post(
                "audio/speech",
                headers={"Authorization": f"Bearer {COGENAI_API_KEY}"},
                json={
                    "model": TTS_MODEL_ID,
                    "input": text_chunk,
                    "voice": TTS_VOICE
                }
            )
            response.raise_for_status()
            
            # Collect chunks into a single bytes object
            mp3_bytes = response.content
            all_audio_chunks.append(mp3_bytes)
            
        except Exception as e:
            print(f"Error processing chunk {chunk_idx + 1}: {e}")
            raise

    # Combine all audio chunks into a single MP3 file
    output_buffer = io.BytesIO()
    for mp3_chunk in all_audio_chunks:
        output_buffer.write(mp3_chunk)
    
    final_mp3 = output_buffer.getvalue()
    print(f"Total audio gen took {time.time()-t:.2f} seconds")
    
    return final_mp3, total_duration
####################


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

@cl.on_audio_start
async def on_audio_start():
    cl.user_session.set("silent_duration_ms", 0)
    cl.user_session.set("is_speaking", False)
    cl.user_session.set("audio_chunks", [])
    cl.user_session.set("video_chunks", [])
    cl.user_session.set("current_audio_response", None)
    return True

#@cl.step(type="tool")
async def speech_to_text(audio_file):
    client = httpx.Client(base_url=COGENAI_URL)
    files = {
        'file': audio_file
    }
    data = {
        "model": "tiny-en"
    }
    response = client.post(
        "audio/transcriptions",
        data=data,
        files=files,
        headers={"Authorization": f"Bearer {COGENAI_API_KEY}"},
        timeout=60
    )
    print("----->", response.text)
    return response.json()

#@cl.step(type="tool")
async def text_to_speech(message, text: str, mime_type: str):
    audio, length = await generate_audio(
        text=text,
        mime_type=mime_type,  # Pass mime_type correctly
        audio_speed=AUDIO_SPEED
    )
    output_audio_el = cl.Audio(
        auto_play=True,
        mime="audio/wav",
        content=audio
    )
    message.elements.append(output_audio_el)

    await message.update()
    # determine the length of the audio
    await asyncio.sleep(length)

    return

async def stream_token(message, token, speed=TEXT_SPEED):
    await message.stream_token(" ")
    for char in token:
        await message.stream_token(f"{char}")
        await cl.sleep(speed)
    await message.update()

async def stream_audio_chunks(message, token):
    text_chunks = split_text(token)
    message.elements = []  # Clear any existing elements
    
    # Keep track of video elements we've created
    audio_elements = []

    for chunk_idx, text_chunk in enumerate(text_chunks):
        print(f"Processing audio chunk {chunk_idx + 1}/{len(text_chunks)}")
        
        # Generate audio for this chunk
        audio, length = await generate_audio(
            text=text_chunk,
            mime_type="wav",
            audio_speed=AUDIO_SPEED
        )
        audio_elements.append(
            cl.Audio(
                auto_play=True,
                mime="audio/wav",
                content=audio
            )
        )
        
        # Update message with all videos generated so far
        message.elements = audio_elements.copy()
        await message.update()
        await asyncio.sleep(length)

    # Final update
    #message.content = ""
    await message.update()

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    audio_chunks = cl.user_session.get("audio_chunks")
    
    if audio_chunks is not None:
        audio_chunk = np.frombuffer(chunk.data, dtype=np.int16)
        audio_chunks.append(audio_chunk)

    # If this is the first chunk, initialize timers and state
    if chunk.isStart:
        cl.user_session.set("last_elapsed_time", chunk.elapsedTime)
        cl.user_session.set("is_speaking", True)
        return

    audio_chunks = cl.user_session.get("audio_chunks")
    last_elapsed_time = cl.user_session.get("last_elapsed_time")
    silent_duration_ms = cl.user_session.get("silent_duration_ms")
    is_speaking = cl.user_session.get("is_speaking")

    # Calculate the time difference between this chunk and the previous one
    time_diff_ms = chunk.elapsedTime - last_elapsed_time
    cl.user_session.set("last_elapsed_time", chunk.elapsedTime)

    # Compute the RMS (root mean square) energy of the audio chunk
    audio_energy = audioop.rms(chunk.data, 2)  # Assumes 16-bit audio (2 bytes per sample)

    if audio_energy < SILENCE_THRESHOLD:
        # Audio is considered silent
        silent_duration_ms += time_diff_ms
        cl.user_session.set("silent_duration_ms", silent_duration_ms)
        if silent_duration_ms >= SILENCE_TIMEOUT and is_speaking:
            cl.user_session.set("is_speaking", False)
            await process_audio()
    else:
        # Audio is not silent, reset silence timer and mark as speaking
        cl.user_session.set("silent_duration_ms", 0)
        if not is_speaking:
            cl.user_session.set("is_speaking", True)

async def process_audio():
    # Get the audio buffer from the session
    if audio_chunks:=cl.user_session.get("audio_chunks"):
       # Concatenate all chunks
        concatenated = np.concatenate(list(audio_chunks))
        
        # Create an in-memory binary stream
        wav_buffer = io.BytesIO()
        
        # Create WAV file with proper parameters
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(24000)  # sample rate (24kHz PCM)
            wav_file.writeframes(concatenated.tobytes())
        
        # Reset buffer position
        wav_buffer.seek(0)
        
        cl.user_session.set("audio_chunks", [])

    frames = wav_file.getnframes()
    rate = wav_file.getframerate()

    duration = frames / float(rate)
    if duration <= 1.00:
        print("The audio is too short, please try again.")
        return

    audio_buffer = wav_buffer.getvalue()

    whisper_input = ("audio.wav", audio_buffer, "audio/wav")
    transcription = await speech_to_text(whisper_input)
    print(transcription)
    message = transcription["text"]

    await cl.Message(
        author="You", 
        type="user_message",
        content=message
    ).send()

    await process_response_avatar(message)

async def process_response_avatar(message: str):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message})

    stream = await llm_client.chat.completions.create(
        model=LLM_MODEL_ID, messages=message_history, stream=True,
    )

    # Show video message first
    text_msg = cl.Message(content="**`🤔 Thinking...`**\n")  # Add thinking indicator with markdown
    await text_msg.send()

    buffer = ""
    current_chunk = ""
    sentence_endings = re.compile(r'([.!?])\s')
    full_response = ""  # Keep track of the full response
    
    async for part in stream:
        token = part.choices[0].delta.content or ""
        buffer += token
        
        # Update thinking indicator while streaming
        if text_msg.content.startswith("**`🤔"):
            text_msg.content = "\n**`✍️ Writing...`**"  # Start with just the writing indicator
            await text_msg.update()
        else:
            # Update the text message with current text + writing indicator
            text_msg.content = f"{full_response}\n"
            await text_msg.update()

        # Check for complete sentences
        while True:
            match = sentence_endings.search(buffer)
            if not match:
                break
            
            sentence = buffer[:match.end()]
            
            # Check if adding this sentence would exceed the limit
            if len(current_chunk) + len(sentence) > SEGMENT_CHUNK_SIZE:
                # Only process if we have a substantial chunk
                if len(current_chunk) > SEGMENT_CHUNK_SIZE * 0.5:  # At least 50% of max size
                    print(f"Processing chunk of length: {len(current_chunk)}")
                    full_response += current_chunk  # Add processed chunk to full response
                    await asyncio.gather(
                        stream_token(message=text_msg, token=current_chunk),
                        stream_audio_chunks(message=text_msg, token=current_chunk)
                    )
                    current_chunk = sentence
                else:
                    current_chunk += sentence
            else:
                current_chunk += sentence
            
            buffer = buffer[match.end():]

    # At end of stream, process any remaining text
    if current_chunk or buffer.strip():
        final_text = (current_chunk + buffer).strip()
        if final_text:
            print(f"Processing final text of length: {len(final_text)}")
            await asyncio.gather(
                stream_token(message=text_msg, token=final_text),
                stream_audio_chunks(message=text_msg, token=final_text)
            )

    # Final updates - remove the writing indicator
    text_msg.content = text_msg.content + "\n\n**`✅ Done!`**"
    await text_msg.update()


@cl.on_message
async def on_message(message: cl.Message):
    await process_response_avatar(message=message.content)
