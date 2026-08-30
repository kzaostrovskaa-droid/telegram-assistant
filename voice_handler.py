import speech_recognition as sr
from pydub import AudioSegment
import os

async def transcribe_voice(file_path: str) -> str:
    audio = AudioSegment.from_file(file_path, format="ogg")
    wav_path = file_path.replace(".ogg", ".wav")
    audio.export(wav_path, format="wav")
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data, language="ru-RU")
    except sr.UnknownValueError:
        text = "Не удалось распознать речь"
    except sr.RequestError:
        text = "Ошибка сервиса распознавания"
    
    if os.path.exists(wav_path):
        os.remove(wav_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return text