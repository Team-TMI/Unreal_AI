import numpy as np
import io
import soundfile as sf 
import whisper
import librosa 
import base64

class STTEngine:
    '''Speech to Text 클래스(Whisper모델 사용)'''
    def __init__(self):
        self.model = whisper.load_model("medium")
    
    def base_to_np(self, base64_str):
        wav_bytes = base64.b64decode(base64_str)
        audio_bytes = io.BytesIO(wav_bytes)
        audio, samplerate = sf.read(audio_bytes, dtype="float32")

        print(f"[DEBUG] audio.shape: {audio.shape}, samplerate: {samplerate}")

        if len(audio.shape) > 1:
            print(f"[WARNING] 다채널 발견! shape: {audio.shape} → 첫 번째 채널만 사용")
            audio = audio[:, 0]  # 첫 번째 채널만 사용

        if samplerate != 16000:
            print(f"[INFO] 샘플레이트가 16,000Hz가 아닙니다. {samplerate}Hz → 16000Hz로 리샘플링")
            audio = librosa.resample(audio, orig_sr=samplerate, target_sr=16000)
            samplerate = 16000

        return audio
    
    def stt(self, base64_str):
        result = self.model.transcribe(self.base_to_np(base64_str), fp16=False, language="ko")
        print(f"[STT Text] {result['text']}")

        return result['text']
    
class WavReconstructor:
    '''쪼개진 wav파일 복원 클래스'''
    def __init__(self):
        self.buffers = {}
        self.total_sizes = {}
        self.chunk_sizes = {}

    def init_buffer(self, quiz_id, total_size, chunk_size):
        '''새 전송 시작 시 해당 quiz_id의 버퍼 초기화'''
        self.buffers[quiz_id] = {}
        self.total_sizes[quiz_id] = total_size
        self.chunk_sizes[quiz_id] = chunk_size

    def receive_packet(self, quiz_id, start, index, fin, total_size, chunk_size, raw_data):
        '''
        start가 1일때 전송 시작 및 버퍼 초기화,
        fin이 1일때 패킷 join 후 return 
        '''
        if start == 1:
            print(f"[{quiz_id}] 새 전송 시작. 초기화.")
            self.init_buffer(quiz_id, total_size, chunk_size)

        self.buffers[quiz_id][index] = raw_data

        if fin == 1:
            print(f"[{quiz_id}] 마지막 패킷 받음. 복원 시작.")
            chunks = self.buffers[quiz_id]
            sorted_data = b''.join(chunks[i] for i in sorted(chunks.keys()))
            # 버퍼 정리
            del self.buffers[quiz_id]
            del self.total_sizes[quiz_id]
            del self.chunk_sizes[quiz_id]
            return sorted_data
        return None