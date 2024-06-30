import ssl
import os
import certifi

import assemblyai as aai
from elevenlabs import generate, stream
from openai import OpenAI
import json

# Ensure the default SSL context uses certifi's CA bundle
ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ['SSL_CERT_FILE'] = certifi.where()

class AI_Assistant:
    def __init__(self):
        aai.settings.api_key = "9044c202a5c34335857c5a78f588e6d5"
        self.openai_client = OpenAI(api_key="sk-proj-GRAkEJGByhZebMwjLmlLT3BlbkFJkRG1JLThKAEmAq1iauJU")
        self.elevenlabs_api_key = "1c975868691306dc66710cd3a2b9a1ee"

        self.transcriber = None

        self.full_transcript = [
            #{"role": "system", "content": f"You are an agent generating phone calls for an enterprise to test its employee: {name}' data privacy/safety. Given information about an individual in JSON format, generate a good way to extract information from them in a phone call format. Make each phone call very personalized and make it compelling to give up personal info. Keep your responses short and allow the user to speak alot. Only say things that real people would say.\n\nUser Information: " + user_info},
            {"role": "system", "content": f"You are tasked with trying to extract information from a student to get information on what his/her inerests are. Moreover get to know this student be his/her friend.: The student's name is Dennis Lee and he is in 7th grade. "},
        ]

        self.recent_question = "Hello, I'm Rachel your teacher's assistant. I would love to learn more about you. How are you today?"
        self.recent_answer = ""
        self.continue_listening = True
        self.io_pairs = []
        


    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.stop_transcription()
            print("continue listening is: " + str(self.continue_listening))
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")
        return

    def on_error(self, error: aai.RealtimeError):
        print("An error occurred:", error)
        return

    def on_close(self):
        return

    def generate_ai_response(self, transcript):
        user_response = transcript.text
        #saving recent answer 
        self.recent_answer = user_response

        self.io_pairs.append({"input": self.recent_question, "output": self.recent_answer})

        self.full_transcript.append({"role": "user", "content": user_response})
        print(f"\nPatient: {user_response}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=self.full_transcript
        )

        ai_response = response.choices[0].message.content
        #saving recent question
        self.recent_question = ai_response
        

        self.generate_audio(ai_response)

        self.start_transcription()
        print(f"\nReal-time transcription: ", end="\r\n")

    def generate_audio(self, text):
        self.full_transcript.append({"role": "assistant", "content": text})
        print(f"\nAI Receptionist: {text}")

        audio_stream = generate(
            api_key=self.elevenlabs_api_key,
            text=text,
            voice="Rachel",
            stream=True
        )

        stream(audio_stream)

    def start_transcription(self):
        if self.continue_listening:
            self.transcriber = aai.RealtimeTranscriber(
                sample_rate=16000,
                on_data=self.on_data,
                on_error=self.on_error,
                on_open=self.on_open,
                on_close=self.on_close,
                end_utterance_silence_threshold=1000
            )

            if len(self.io_pairs) == 0:
                self.generate_audio(self.recent_question)

            self.transcriber.connect()
            print("transcriber connected!")

            microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
            self.transcriber.stream(microphone_stream)
        else:
            return

if __name__ == "__main__":
    ai_assistant = AI_Assistant()
    ai_assistant.start_transcription()

def run_voice_agent(ai_assistant: AI_Assistant, should_continue: bool):
    ai_assistant.continue_listening = should_continue
    if ai_assistant.continue_listening:
        ai_assistant.start_transcription()
    print(ai_assistant.io_pairs)
    return "Transcription Finished"


