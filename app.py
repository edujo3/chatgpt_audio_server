# app.py
from flask import Flask, request, send_file
from gtts import gTTS
import openai
import os
import uuid

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "Servidor activo y esperando audio."

@app.route('/procesar_audio', methods=['POST'])
def procesar_audio():
    if 'audio' not in request.files:
        return "No se encontró el archivo de audio.", 400

    audio_file = request.files['audio']
    audio_path = f"/tmp/{uuid.uuid4()}.wav"
    audio_file.save(audio_path)

    # Simulación STT (real: usar Whisper, SpeechRecognition, etc.)
    texto_simulado = "Hola, ¿cómo estás?"

    # Enviar a ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": texto_simulado}]
    )
    respuesta_texto = response.choices[0].message.content.strip()

    # Convertir a audio
    tts = gTTS(respuesta_texto, lang='es')
    
    respuesta_path = "/tmp/respuesta.mp3"
    tts.save(respuesta_path)

    return send_file(respuesta_path, mimetype="audio/mpeg")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
