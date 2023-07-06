# Holographic-3D
Its a virtual asistant maked with Unity, OpenAI API.

There is two branch, the firs one is the Server Flask, its content a json file and the Flask file, allows the conection to OpenAI API to request the answer from ChatGPT.
The last one is the Unity Project, its content the Avatar 3d Model to the transmition to the HoloLens 2.
In the Unity Project there is the Holographic model, you can ask the question and the Model answer in real time.


The Flask file is a web application written in Python using the Flask framework. The application performs a series of tasks related to audio and text processing using different services and APIs.
Start with the API Key Configuration:

The OpenAI (openai_api_key) and ElevenLabs (eleven_api_key) API keys are configured to authenticate requests to the corresponding services.

Configuration of the chat and voice model:
chatgpt_model specifies the OpenAI chat model to use.
chatgpt_system is a system message that will be sent as part of the conversation with the model.
voice_list contains a list of voices available for Text-to-Speech.
selected_voice_index is the index of the selected voice in the list.
selected_voice_id is the voice ID corresponding to the selected voice.
Flask app settings:

An instance of the Flask class is created with the name of the application, and the static folder is specified.
Error logging is configured to a file called "app.log".
Auxiliary functions: convert_to_wav(input_file): Converts an audio file in PCM format to a mono WAV file using the FFMPEG tool.
transcribe_audio(file_path): Uses the Google Cloud Speech-to-Text API to transcribe an audio file into text.
get_gpt4_response(prompt): Uses the OpenAI chat model to get a response from a given prompt.
get_audio_from_text(text): Uses the ElevenLabs API to generate an audio file from a given text.
convert_mp3_to_wav(input_file): Converts an audio file in MP3 format to a WAV file using the FFMPEG tool.
Path /upload:

The upload_file() function handles POST requests to the /upload path.
The function receives an audio file, saves it to the server, and performs a series of processing steps.
It uses the helper functions mentioned above to convert the audio format, transcribe it, get a GPT-3 response, and generate an audio file from the response.
The resulting audio file is saved in the application's static folder.
Finally, it returns the URL of the resulting audio file.
