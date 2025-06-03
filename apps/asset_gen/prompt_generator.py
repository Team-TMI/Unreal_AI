from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from pathlib import Path
import openai

# .env 로드 (backend 디렉토리 기준)
load_dotenv(dotenv_path=Path("backend/.env"))
openai.api_key = os.getenv("OPENAI_API_KEY")

# LLM 초기화
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

# 프롬프트 템플릿 정의
prompt_template = ChatPromptTemplate.from_template("""
Based on the following description, create a prompt text to create a 3D-style image.
Conditions:
- Write in English
- Include the style '3D rendered, soft lighting, isometric view, high detail'
- Background should have a transparent or solid color feel
-  Remove prefixes like “Prompt:” and only output pure prompt sentences
                                                   
Description: {description}
""")

# 최종 함수
def generate_3d_prompt(description: str) -> str:
    chain = prompt_template | llm
    result = chain.invoke({"description": description})
    return result.content.strip().replace("Prompt:", "").strip()
