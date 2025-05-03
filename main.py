from fastapi import FastAPI, File, UploadFile
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/voice")
async def receive_audio(file: UploadFile = File(...)):
    # Guardar el archivo recibido
    file_location = f"temp_audio/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Enviar a OpenAI Whisper para transcripción (usa el modelo whisper-1)
    audio_file = open(file_location, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    print("Usuario dijo:", transcript['text'])

    # Enviar la transcripción a ChatGPT
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": transcript['text']
        }]
    )

    response_text = completion.choices[0].message.content
    print("Respuesta GPT:", response_text)

    return {"response": response_text}
