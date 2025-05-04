from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from openai import OpenAI
from gtts import gTTS
import tempfile
import os

client = OpenAI()  # Usará la variable de entorno OPENAI_API_KEY

app = FastAPI()

@app.get("/")
def index():
    return {"status": "Servidor ChatGPT por voz activo ✅"}

@app.post("/audio")
async def audio_to_chat(audio: UploadFile = File(...)):
    try:
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(await audio.read())
            temp_audio_path = temp_audio.name

        # Transcribir
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(temp_audio_path, "rb")
        )
        texto_usuario = transcript.text

        # Consulta a ChatGPT
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional que responde con empatía."},
                {"role": "user", "content": texto_usuario}
            ]
        )
        texto_respuesta = respuesta.choices[0].message.content

        # Generar respuesta en audio
        respuesta_audio_path = "respuesta.mp3"
        tts = gTTS(text=texto_respuesta, lang="es")
        tts.save(respuesta_audio_path)

        return FileResponse(respuesta_audio_path, media_type="audio/mpeg")

    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
