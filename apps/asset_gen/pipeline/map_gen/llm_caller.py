from dotenv import load_dotenv
import os
from pathlib import Path
import openai

# 경로를 명시적으로 설정
load_dotenv(dotenv_path = Path("backend/.env"))

def call_llm(prompt: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "너는 플랫폼 점프맵 설계자야"},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ LLM 호출 오류:", e)
        return "[]"
