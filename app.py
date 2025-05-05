from flask import Flask, request, send_file
from gtts import gTTS
import tempfile
import os
import openai
from datetime import datetime

app = Flask(__name__)

# Reemplaza con tu clave real de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return "🟢 Servidor de voz activo"

@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    if not request.data:
        return "❌ No se recibió audio", 400

    # Guarda el audio recibido en un archivo temporal .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        temp_wav.write(request.data)
        temp_wav_path = temp_wav.name

    try:
        # Transcripción con Whisper
        with open(temp_wav_path, "rb") as f:
            transcription = openai.Audio.transcribe(
                model="whisper-1",
                file=f,
                language="es"
            )
        texto = transcription["text"]
        print("📝 Texto transcrito:", texto)

        # Respuesta generada por ChatGPT
        respuesta = generar_respuesta_chatgpt(texto)
        print("💬 Respuesta:", respuesta)

        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"respuesta_{timestamp}.mp3"
        output_path = os.path.join(tempfile.gettempdir(), filename)

        # Texto a voz con gTTS
        tts = gTTS(text=respuesta, lang='es')
        tts.save(output_path)

        # Devuelve el archivo MP3 generado con nombre consistente
        return send_file(
            output_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print("❌ Error:", str(e))
        return f"❌ Error: {str(e)}", 500
    finally:
        os.remove(temp_wav_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

def generar_respuesta_chatgpt(texto_usuario):
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente emocional amable y empático."},
            {"role": "user", "content": texto_usuario}
        ]
    )
    return respuesta["choices"][0]["message"]["content"]
