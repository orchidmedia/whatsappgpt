import os
import requests
import tempfile
import uuid
import openai
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
import base64

load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_TOKEN')
client = Client(account_sid, auth_token)

sid_encoded = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8"))
sid_encoded = sid_encoded.decode("utf-8")

def chat_completion(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  
        messages=[
            {"role": "system", "content": "Your name is Jarvis, a very formal AI assistant. Keep every answer up to 1200 characters LIMIT. This is very important."},
            {"role": "user", "content": "Always keep the answer to a 1200 character limit, always."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

#Dalle Option DO NOT DELETE WILL USE LATER
#def create_image(prompt: str) -> str:
    completion = openai.Completion.create(
        model="dall-e-3",
        prompt=f"Create an image based on {prompt}",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return completion.choices[0].text.strip()

def create_image(prompt: str) -> str:
    completion =openai.Image.create (
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return completion['data'][0]['url']

def transcript_audio(media_url: str) -> str:
    try:
        ogg_file_path = f'{tempfile.gettempdir()}/{uuid.uuid1()}.ogg'
        basic_header = "Basic {}".format(sid_encoded)
        response = requests.get(media_url, stream=True, headers={
            "Authorization": basic_header
        })
        if response.status_code != 200:
            return f"Failed to download the file. Status code: {response.status_code}"

        with open(ogg_file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192): 
                    file.write(chunk)

        with open(ogg_file_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                'whisper-1', audio_file, api_key=os.getenv('OPENAI_API_KEY'))
            print(transcript)
            return transcript['text']
    except Exception as e:
        return f'Error at transcript_audio: {e}'

    finally:
        if os.path.exists(ogg_file_path):
            os.unlink(ogg_file_path)