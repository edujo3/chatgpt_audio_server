from flask import Flask, request, jsonify, send_file
import openai
import tempfile
from gtts import gTTS
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")  # Usa tus variables de entorno

@app.route("/")
def index():
    return "Servidor ChatGPT por Voz está activo ✅"

@app.route("/audio", methods=["POST"])
def audio_to_chat():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]
    
    # Guarda archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    try:
        # Transcripción con Whisper
        transcript = openai.Audio.transcribe("whisper-1", open(temp_audio_path, "rb"))
        texto_usuario = transcript["text"]

        # Consulta a ChatGPT
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional que escucha al usuario y le responde con empatía, lo orientaen el tema psicológico y emocional. No abordas otros temas diferentes."},
                {"role": "user", "content": texto_usuario}
            ]
        )
        texto_respuesta = respuesta.choices[0].message["content"]

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
    app.run(debug=True)
