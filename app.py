from flask import Flask, request, send_file
from gtts import gTTS
import openai
import os
import uuid

app = Flask(__name__)

# Obtener la API Key desde las variables de entorno (Railway)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "🟢 Servidor activo y esperando audio"

@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    if 'audio' not in request.files:
        return "❌ Archivo 'audio' no encontrado", 400

    audio_file = request.files['audio']
    audio_file.seek(0)  # Asegura que el puntero esté al inicio del archivo

    try:
        # 🎙️ Transcripción con Whisper
        whisper_response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="es"
        )
        texto_transcrito = whisper_response["text"]
        print(f"📝 Texto transcrito: {texto_transcrito}")
    except Exception as e:
        return f"❌ Error al transcribir con Whisper: {str(e)}", 500

    try:
        # 💬 Envío del texto a ChatGPT
        chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional que responde de forma empática."},
                {"role": "user", "content": texto_transcrito}
            ]
        )
        respuesta_texto = chat_response.choices[0].message.content.strip()
        print(f"🤖 Respuesta de ChatGPT: {respuesta_texto}")
    except Exception as e:
        return f"❌ Error al generar respuesta de ChatGPT: {str(e)}", 500

    try:
        # 🔊 Conversión a audio (respuesta.mp3)
        tts = gTTS(respuesta_texto, lang="es")
        respuesta_path = "/tmp/respuesta.mp3"
        tts.save(respuesta_path)
    except Exception as e:
        return f"❌ Error al generar el audio con gTTS: {str(e)}", 500

    # 📤 Enviar archivo MP3 al ESP32
    return send_file(respuesta_path, mimetype="audio/mpeg")

# Modo local o debug
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
