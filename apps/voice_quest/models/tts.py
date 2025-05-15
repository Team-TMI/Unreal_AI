from google.cloud import texttospeech
from dotenv import load_dotenv
load_dotenv()

class TTSEngine:
    '''Text to Speech 클래스(Google Cloud TTS모델 사용)'''
    def __init__(self):
        self.audio_dir = "C:/wanted/Git_project/Unreal_AI/apps/voice_quest/data/audio"
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code = "ko-KR",
            name = "ko-KR-Standard-B"
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

    def response(self,text):
        input_text = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input = input_text,
            voice = self.voice,
            audio_config=self.audio_config
        )
        return response