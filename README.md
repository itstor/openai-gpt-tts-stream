# GPT to TTS Stream using Flask

Stream responses from GPT directly to the OpenAI TTS. To make the response faster, it chunks the GPT responses into sentences, sending these to the TTS, and then streaming the audio back to the client. It uses opus audio encoding to reduce the size of the audio stream.
