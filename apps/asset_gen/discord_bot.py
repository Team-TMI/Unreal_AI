import discord
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from prompt_generator import generate_3d_prompt
from pipeline.generate_png import generate_image_from_prompt  # Stable Diffusion 실행용

import requests
import json
import re

from openai import OpenAI

# .env 로드 (backend 디렉토리 기준)
load_dotenv(dotenv_path=Path("backend/.env"))
openapi = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def call_llm(prompt: str):
#     # pipeline/map_gen/prompt_pattern_based.txt
#     BASE_DIR = Path(__file__).resolve().parent
#     # /home/wanted-1/potenup-workspace/Project/Final_Project/team2/JM/asset_gen/pipeline/map_gen/prompt_pattern_based.txt
#     DATA_PATH = BASE_DIR / "pipeline" / "map_gen" / "prompt_pattern_based.txt"
#     system_prompt = open(DATA_PATH, "r", encoding="utf-8").read()

#     # print(system_prompt)

#     response = openapi.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": prompt}
#         ]
#     )
    
#     print(response)
#     raw = response.choices[0].message.content
#     print(f"raw: {raw}")
    
#     try:
#         result = re.search(r'\[.*\]', raw, re.DOTALL)
#         sections = json.loads(result)
#     except json.JSONDecodeError as e:
#         print(f"JSON decode error: {e}")
#         print(f"json_str: {json_str}")

#     return json.loads(re.search(r'\[.*\]', raw, re.DOTALL)[0])

def call_llm(prompt: str):
    BASE_DIR = Path(__file__).resolve().parent
    DATA_PATH = BASE_DIR / "pipeline" / "map_gen" / "prompt_pattern_based.txt"
    system_prompt = open(DATA_PATH, "r", encoding="utf-8").read()

    response = openapi.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    print(f"raw: {raw}")

    try:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if not match:
            raise ValueError("❌ LLM 응답에서 JSON 배열을 찾을 수 없습니다.")
        
        json_str = match.group()
        sections = json.loads(json_str)
        return sections

    except Exception as e:
        print(f"❌ LLM JSON 파싱 실패: {e}")
        print(f"raw LLM output: {raw}")
        return []  # 또는 raise

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

# MAP_API_URL = "http://localhost:8000/service3/generate_map_sections"
MAP_API_URL = "http://localhost:8000/generate_map_sections"


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 1. 텍스처 생성
    if message.content.startswith("!generate "):
        description = message.content.replace("!generate ", "").strip()
        await message.channel.send(f"🧠 '{description}' 설명으로 프롬프트 생성 중...")

        prompt = generate_3d_prompt(description)
        await message.channel.send(f"🎨 생성된 프롬프트:\n```{prompt}```")

        image_path = generate_image_from_prompt(prompt)
        await message.channel.send(file=discord.File(image_path))

    # 2. 맵 생성
    elif message.content.startswith("!map "):
        description = message.content.replace("!map ", "").strip()
        await message.channel.send(f"🧱 '{description}' 맵 생성 중...")
        sections = call_llm(description)
        res = requests.post(MAP_API_URL, json={"sections": sections})

        print(res)
        try:
            # res = requests.post(MAP_API_URL, json={"prompt": description})
            
            if res.status_code != 200:
                await message.channel.send(f"❌ 서버 오류: {res.text}")
                return

            result = res.json()
            print(result)
            
            if "json_path" not in result:
                await message.channel.send(f"❌ 예상치 못한 응답 형식: {result}")
                return
            json_url = result["json_path"]
            preview_path = result["preview_image"].replace("/result/", "backend/outputs/")
            json_path = json_url.replace("/result/", "backend/outputs/")

            # await message.channel.send(
            #     f"✅ 맵 타입: `{result['used_type']}`\n"
            #     f"📐 파라미터: `{result['used_parameters']}`"
            # )

            # 전송: 이미지 + JSON 파일 둘 다 첨부
            await message.channel.send(files=[
                discord.File(preview_path),
                discord.File(json_path)
            ])

        except Exception as e:
            await message.channel.send(f"❌ 오류 발생: {str(e)}")

client.run(DISCORD_TOKEN)