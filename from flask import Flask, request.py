from flask import Flask, request
from werkzeug.utils import secure_filename
from google.cloud import speech
import os
import subprocess
import logging
import openai
import requests
import tempfile
from elevenlabs import generate, set_api_key, voices

# Configure GPT-4 and Text-to-speech API keys
openai_api_key = "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"
eleven_api_key = "eb07ce5f316673f15a4c6967aa485b80"

openai.api_key = openai_api_key
set_api_key(eleven_api_key)

chatgpt_model = "gpt-3.5-turbo"
chatgpt_system = "eres una dulce persona amable que se llama ana"
voice_list = voices()
selected_voice_index = 1  # Modify this with the index of your chosen voice
selected_voice_id = voice_list[selected_voice_index].voice_id

app = Flask(__name__, static_folder='static')

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

def convert_to_wav(input_file):
    output_file = "converted_audio.wav"
    output_file_path = os.path.join(app.root_path, output_file)

    # Delete the existing WAV file if it exists
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    # Convert the input PCM file to mono WAV
    subprocess.run(["ffmpeg", "-f", "s16le", "-ar", "44100", "-ac", "2", "-i", input_file, "-ac", "1", output_file_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def transcribe_audio(file_path):
    client = speech.SpeechClient()

    with open(os.path.join(app.root_path, file_path), "rb") as audio_file:
        input_audio = audio_file.read()

    audio = speech.RecognitionAudio(content=input_audio)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="es-ES",
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript

def get_gpt4_response(prompt):
    response = openai.ChatCompletion.create(
        model=chatgpt_model,
        messages=[
            {"role": "system", "content": chatgpt_system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_audio_from_text(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + selected_voice_id

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_api_key
    }

    data = {
        "text": text,
        "model_id" : "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 1.0
        }
    }

    response = requests.post(url, json=data, headers=headers)

    # Save audio data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in response.iter_content():
            if chunk:
                f.write(chunk)
        f.flush()
        return f.name

def convert_mp3_to_wav(input_file):
    output_file = "output.wav"
    output_file_path = os.path.join(app.static_folder, output_file)
    subprocess.run(["ffmpeg", "-y", "-i", input_file, output_file_path])

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, filename)
        file.save(file_path)

        try:
            convert_to_wav(file_path)
            transcript = transcribe_audio("converted_audio.wav")
            print(f"Transcript: {transcript}")  # print the transcript
            gpt_response = get_gpt4_response(transcript)
            mp3_file = get_audio_from_text(gpt_response)
            convert_mp3_to_wav(mp3_file)
            return 'http://127.0.0.1:5000/static/output.wav'
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            return str(e)

if __name__ == '__main__':
    app.run(debug=True)
