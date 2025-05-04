from flask import Flask, request, jsonify, send_file
from openai import OpenAI
from gtts import gTTS
import tempfile
import os
import io

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Asegúrate de que esté definido en Railway

@app.route("/")
def index():
    return "Servidor ChatGPT por Voz está activo ✅"

@app.route("/audio", methods=["POST"])
def audio_to_chat():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]
    
    # Lee el contenido en memoria para pasarlo a OpenAI
    audio_bytes = audio_file.read()
    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.name = "audio.wav"  # Nombre ficticio requerido por la API

    try:
        # Transcripción con Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream
        )
        texto_usuario = transcript.text

        # Genera la respuesta con ChatGPT
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional que escucha con empatía."},
                {"role": "user", "content": texto_usuario}
            ]
        )
        texto_respuesta = respuesta.choices[0].message.content

        # Convertir texto a audio con gTTS
        tts = gTTS(text=texto_respuesta, lang="es")
        respuesta_path = "respuesta.mp3"
        tts.save(respuesta_path)

        return send_file(respuesta_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
