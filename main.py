from flask import Flask, Response, request, jsonify, stream_with_context
from openai import OpenAI
from dotenv import load_dotenv
import os
import json


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)

openaiClient = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def api_error(message, status_code):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    content = data.get('content')

    if not content:
        return api_error("\"content\" field is required", 400)

    response = openaiClient.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="gpt-3.5-turbo",
        stream=True
    )

    def generate():
        retrieved = ''
        sentences = ''
        for chunk in response.response.iter_bytes(1024):
            if chunk:
                retrieved += chunk.decode('utf-8')
                if '\n\n' in retrieved:
                    *completed, retrieved = retrieved.split('\n\n')
                    for json_object in completed:
                        json_object = json_object.replace('data: ', '').strip()
                        if json_object == '[DONE]':
                            continue
                        try:
                            if json_object:
                                json_data = json.loads(json_object)
                                text = json_data.get('choices', [{}])[0].get(
                                    'delta', {}).get('content', '')
                                sentences += text
                                if sentences and sentences.endswith('.' or '!' or '?'):

                                    audio_response = openaiClient.audio.speech.create(
                                        model="tts-1",
                                        voice="nova",
                                        input=sentences,
                                        response_format="opus"
                                    )

                                    sentences = ''

                                    for audio_chunk in audio_response.iter_bytes(1024):
                                        yield audio_chunk

                        except json.JSONDecodeError as e:
                            print(e)
                            continue

    return Response(stream_with_context(generate()), content_type='audio/opus')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
