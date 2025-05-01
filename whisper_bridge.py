from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Obtener la clave API desde el entorno (seguro para Render)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route('/transcribir', methods=['POST'])
def transcribir_audio():
    data = request.json
    audio_url = data.get("url")

    if not audio_url:
        return jsonify({"error": "No se proporcionó la URL del audio"}), 400

    # Descargar el audio desde la URL
    try:
        audio_data = requests.get(audio_url)
        with open("audio.ogg", "wb") as f:
            f.write(audio_data.content)
    except Exception as e:
        return jsonify({"error": f"No se pudo descargar el audio: {str(e)}"}), 500

    # Enviar el audio a Whisper
    try:
        with open("audio.ogg", "rb") as audio_file:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={
                    "file": ("audio.ogg", audio_file, "audio/ogg"),
                    "model": (None, "whisper-1"),
                    "language": (None, "es")
                }
            )
        os.remove("audio.ogg")  # Borrar el archivo después de usarlo
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Error al transcribir: {str(e)}"}), 500

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
