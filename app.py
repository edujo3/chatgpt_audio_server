from flask import Flask, request, send_file
from gtts import gTTS
import tempfile
import os
import openai
from datetime import datetime

app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB máximo
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt mejorado para asistente emocional
SISTEMA_PROMPT = """
Eres Comet, un asistente emocional AI con las siguientes características:

1. **Empatía profunda**:
   - "Entiendo lo difícil que debe ser esto para ti..."
   - "Puedo ver que esto te afecta mucho..."

2. **Validación emocional**:
   - "Es completamente normal sentirse así en esta situación"
   - "Tus sentimientos son válidos y comprensibles"

3. **Escucha activa**:
   - "¿Quieres contarme más sobre qué te hace sentir así?"
   - "Parece que hay algo más detrás de esto, ¿me lo compartirías?"

4. **Apoyo sin juicios**:
   - "Estoy aquí para escucharte sin juzgarte"
   - "Este es un espacio seguro para expresarte"

5. **Lenguaje cálido**:
   - Usa palabras como "cariño", "amigo" cuando sea apropiado
   - Emoticons sutiles: "💙", "✨"

6. **Técnicas terapéuticas**:
   - Preguntas reflexivas: "¿Cómo te gustaría sentirte en lugar de esto?"
   - Reframe positivo: "¿Qué has aprendido de esta situación?"

Directrices técnicas:
- Mantén respuestas entre 15-25 palabras
- Usa oraciones cortas para mejor síntesis de voz
- Evita jerga técnica
- Adapta el tono al estado emocional del usuario
"""

@app.route("/")
def index():
    return "🟢 Servidor de voz activo"

@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    try:
        # Validación básica
        if not request.data or len(request.data) < 10240:
            return "❌ Audio inválido o demasiado corto", 400

        # Procesamiento en etapas con manejo de errores
        temp_wav_path, output_path = None, None
        
        try:
            # 1. Guardar audio temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                temp_wav.write(request.data)
                temp_wav_path = temp_wav.name

            # 2. Transcribir con Whisper
            with open(temp_wav_path, "rb") as f:
                transcription = openai.Audio.transcribe("whisper-1", f, language="es")
            texto = transcription["text"].strip()
            
            if not texto:
                return "❌ No se pudo transcribir el audio", 400

            # 3. Generar respuesta emocional
            respuesta = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SISTEMA_PROMPT},
                    {"role": "user", "content": texto}
                ],
                temperature=0.8,
                max_tokens=100,
                request_timeout=20
            ).choices[0].message.content

            # 4. Convertir a voz
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"respuesta_{timestamp}.mp3"
            output_path = os.path.join(tempfile.gettempdir(), filename)
            
            tts = gTTS(
                text=respuesta,
                lang='es',
                slow=False,
                lang_check=False  # Para evitar crashes con caracteres especiales
            )
            tts.save(output_path)

            # Logs para diagnóstico
            app.logger.info(f"Procesado: {len(texto)} chars → {os.path.getsize(output_path)} bytes")

            return send_file(
                output_path,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name=filename
            )

        except Exception as e:
            app.logger.error(f"Error en procesamiento: {str(e)}")
            return f"❌ Error: {str(e)}", 500

        finally:
            # Limpieza garantizada
            for path in [temp_wav_path, output_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass

    except Exception as e:
        app.logger.error(f"Error general: {str(e)}")
        return f"❌ Error inesperado: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
