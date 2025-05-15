
## 주요 컴포넌트 설명
### 1. 벡터DB 생성
- `vector_db.py` 또는 `test.ipynb`에서 PDF(`data/PDF/Epilogue.pdf`)를 로드
- [키워드] 단위로 문서 분할, chunk로 쪼개어 Chroma DB에 저장
- 임베딩: OpenAIEmbeddings 사용

### 2. LLM 프롬프트
- `prompts/quiz.prompt`: 퀴즈(한 문장, 정답 직접 언급 금지, 따뜻한 말투)
- `prompts/hint.prompt`: 힌트(2~3문장, 정답 직접 언급/초성/글자수 금지, 오답시 부드럽게 안내)

### 3. WebSocket API
- `/voice_quest` 엔드포인트
- 퀴즈 시작(QuizNotify) → 음성 답변(WaveRequest) → STT 변환 → 정답 평가/힌트 생성 → 응답

### 4. 주요 클래스
- `Quiz`: 퀴즈 생성 LLM
- `Hint`: 힌트 생성 LLM, 세션별 대화 기록 관리, 유사도/정답 포함 여부 평가
- `STTEngine`: Whisper로 음성→텍스트 변환
- `WavReconstructor`: 쪼개진 오디오 패킷 복원

### 5. 유틸리티
- `shared/utills.py`: 세션 관리, 오디오 저장 등

## 실행 방법
1. 환경 변수 설정: `.env` 파일에 OpenAI, Google API 키 등 입력
2. PDF→벡터DB 변환: `python vector_db.py` 실행
3. FastAPI 서버 실행: `python main.py`
4. WebSocket 클라이언트로 `/voice_quest` 접속 및 음성 퀴즈 진행

## 참고/의존성
- Python 3.10+
- FastAPI, Uvicorn, LangChain, Chroma, Whisper, Google Cloud TTS 등
- 상세 코드는 `test.ipynb` 및 각 모듈 참고