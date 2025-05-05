from flask import Flask, request, send_file
from gtts import gTTS
import tempfile
import os
import openai
from datetime import datetime

app = Flask(__name__)

# Configuración de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return "🟢 Servidor de voz activo"

@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    if not request.data:
        return "❌ No se recibió audio", 400

    # Validación tamaño mínimo del audio
    if len(request.data) < 10240:
        return "❌ Audio demasiado corto", 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            temp_wav.write(request.data)
            temp_wav.flush()
            temp_wav_path = temp_wav.name
        
        if os.path.getsize(temp_wav_path) < 10240:
            raise ValueError("Archivo WAV demasiado pequeño")

        # Transcripción
        with open(temp_wav_path, "rb") as f:
            transcription = openai.Audio.transcribe("whisper-1", f, language="es")
        texto = transcription["text"].strip()
        
        if not texto or len(texto) < 3:
            raise ValueError("Transcripción vacía o muy corta")

        # Generar respuesta emocional
        respuesta = generar_respuesta_chatgpt(texto)
        if not respuesta or len(respuesta) < 5:
            raise ValueError("Respuesta de ChatGPT inválida")

        # Generar MP3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"respuesta_{timestamp}.mp3"
        output_path = os.path.join(tempfile.gettempdir(), filename)
        
        tts = gTTS(text=respuesta, lang='es', slow=False)
        tts.save(output_path)

app.logger.info(f"Tamaño WAV recibido: {len(request.data)} bytes")
app.logger.info(f"Tamaño MP3 generado: {os.path.getsize(output_path)} bytes")
app.logger.info(f"Duración estimada audio: {os.path.getsize(output_path)/3200:.2f} segundos")

        if os.path.getsize(output_path) < 10240:
            raise ValueError("Archivo MP3 demasiado pequeño")

        response = send_file(
            output_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=filename
        )
        return response

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return f"❌ Error: {str(e)}", 500
    finally:
        for path in [temp_wav_path, output_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

def generar_respuesta_chatgpt(texto_usuario):
    sistema_prompt = """
    Eres un asistente emocional llamado Comet. Tu misión es proporcionar apoyo emocional mediante:
    1. Validación emocional: "Entiendo que esto debe ser difícil para ti..."
    2. Escucha activa: "¿Quieres contarme más sobre cómo te hace sentir esto?"
    3. Normalización: "Es humano sentirse así en estas situaciones..."
    4. Empatía cognitiva: "Por lo que me dices, parece que te sientes..."
    5. Apoyo incondicional: "Estoy aquí para escucharte sin juzgarte..."

    Directrices:
    - Usa lenguaje cálido pero profesional
    - Limita respuestas a 2-3 frases
    - Adapta tu tono al estado emocional del usuario
    - Evita dar consejos no solicitados
    - Haz preguntas abiertas cuando sea apropiado
    """
    
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": sistema_prompt},
            {"role": "user", "content": texto_usuario}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return respuesta["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
