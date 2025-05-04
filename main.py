from flask import Flask, request, jsonify, send_file
from openai import OpenAI
from gtts import gTTS
import tempfile
import os

app = Flask(__name__)

# ✅ Inicializa el cliente con la API key desde las variables de entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return "Servidor ChatGPT por Voz está activo ✅"

@app.route("/audio", methods=["POST"])
def audio_to_chat():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    try:
        # Transcripción con Whisper
        with open(temp_audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )

        texto_usuario = transcript.strip()

        # Consulta a ChatGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional que escucha al usuario y le responde con empatía, lo orienta en el tema psicológico y emocional. No abordas otros temas diferentes."},
                {"role": "user", "content": texto_usuario}
            ]
        )
        texto_respuesta = response.choices[0].message.content

        # Convierte texto en audio
        tts = gTTS(text=texto_respuesta, lang="es")
        respuesta_audio_path = "respuesta.mp3"
        tts.save(respuesta_audio_path)

        return send_file(respuesta_audio_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        os.remove(temp_audio_path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
