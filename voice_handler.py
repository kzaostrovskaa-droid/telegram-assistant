import os
import openai
from config import OPENAI_API_KEY

client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def transcribe_voice(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"
            )
        return response.text
    except Exception as e:
        return f"Ошибка распознавания: {e}"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)