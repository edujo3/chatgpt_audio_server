from flask import Flask, request, send_file
from gtts import gTTS
import tempfile
import os
import openai
from pydub import AudioSegment  # 🔄 Necesario para convertir MP3 a WAV

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return "🟢 Servidor de voz activo"

@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    if not request.data:
        return "❌ No se recibió audio", 400

    # Guarda audio recibido
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

        # Respuesta ChatGPT
        respuesta = generar_respuesta_chatgpt(texto)
        print("💬 Respuesta:", respuesta)

        # Generar MP3 con gTTS
        mp3_path = os.path.join(tempfile.gettempdir(), "respuesta.mp3")
        wav_path = os.path.join(tempfile.gettempdir(), "respuesta.wav")
        gTTS(text=respuesta, lang='es').save(mp3_path)

        # Convertir MP3 a WAV (16-bit, mono, 16kHz)
        audio = AudioSegment.from_mp3(mp3_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(wav_path, format="wav")

        # Enviar WAV al ESP32
        return send_file(wav_path, mimetype="audio/wav")

    except Exception as e:
        print("❌ Error:", str(e))
        return f"❌ Error: {str(e)}", 500
    finally:
        os.remove(temp_wav_path)

def generar_respuesta_chatgpt(texto_usuario):
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente emocional amable y empático."},
            {"role": "user", "content": texto_usuario}
        ]
    )
    return respuesta["choices"][0]["message"]["content"]
