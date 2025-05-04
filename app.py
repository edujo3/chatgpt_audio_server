from flask import Flask, request, send_file
from gtts import gTTS
import openai
import os
import uuid

app = Flask(__name__)

# Clave de OpenAI desde variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "🟢 Servidor activo y esperando audio"

@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    if 'audio' not in request.files:
        return "❌ Archivo 'audio' no encontrado", 400

    audio_file = request.files['audio']
    
    # Guardar temporalmente el audio
    audio_filename = f"/tmp/{uuid.uuid4()}.wav"
    audio_file.save(audio_filename)

    # 🧠 Aquí deberías hacer el reconocimiento de voz (STT)
    # Esta parte está simulada por ahora
    texto_simulado = "Hola, ¿cómo estás?"

    # Enviar texto a ChatGPT
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional que responde de forma empática."},
                {"role": "user", "content": texto_simulado}
            ]
        )
        respuesta_texto = respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error en ChatGPT: {str(e)}", 500

    # Convertir respuesta a audio con gTTS
    try:
        tts = gTTS(respuesta_texto, lang="es")
        respuesta_path = "/tmp/respuesta.mp3"
        tts.save(respuesta_path)
    except Exception as e:
        return f"❌ Error al generar audio: {str(e)}", 500

    return send_file(respuesta_path, mimetype="audio/mpeg")

# Para correr en local o debug
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
