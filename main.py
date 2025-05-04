from flask import Flask, request, jsonify, send_file
from openai import OpenAI
from gtts import gTTS
import tempfile
import os

app = Flask(__name__)
client = OpenAI()  # Cliente actualizado

@app.route("/")
def index():
    return "Servidor ChatGPT por Voz activo ✅"

@app.route("/audio", methods=["POST"])
def audio_to_chat():
    if "audio" not in request.files:
        return jsonify({"error": "No se recibió archivo de audio"}), 400

    audio_file = request.files["audio"]
    
    # Guardar archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    try:
        # Transcripción usando nuevo cliente
        with open(temp_audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        
        texto_usuario = transcript.text

        # Generar respuesta de ChatGPT
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente emocional..."},
                {"role": "user", "content": texto_usuario}
            ]
        )

        texto_respuesta = respuesta.choices[0].message.content

        # Convertir a audio
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
