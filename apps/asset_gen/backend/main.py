from uuid import uuid4
import os
import json
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import UploadFile, File
from pydantic import BaseModel

import base64
import io
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List

from backend.enum_map import season_enum
from backend.blip_infer import infer_season_from_image
import httpx

from pipeline.base_generator import BaseTextureGenerator
from pipeline.lora_manager import load_lora_pipeline
from pipeline.map_gen.map_generator import MapGenerator 
from pipeline.map_gen.prompt_parser import parse_prompt
from pipeline.map_gen.object_parser import ObjectParser

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# app = FastAPI(root_path="/service3")
app = FastAPI()


# CORS 허용 (Streamlit이 프론트라면 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class GenerateRequest(BaseModel):
    prompt: str
    seed: int = 42
    mode: str = "albedo"

@app.post("/generate_quadrant")
def generate_texture(data: GenerateRequest):
    output_dir = "backend/outputs"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{data.mode}_{uuid4().hex[:8]}.png"
    output_path = os.path.join(output_dir, filename)

    try:
        lora_path = "gokaygokay/Flux-Seamless-Texture-LoRA"
        pipe = load_lora_pipeline(lora_path=lora_path)
        generator = BaseTextureGenerator(mode=data.mode)
        
        generator.apply_lora("gokaygokay/Flux-Seamless-Texture-LoRA")
        generator.generate_quadrant_texture(data.prompt, output_path=output_path, seed=data.seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"생성 실패: {str(e)}")

    return {"image_path": f"/result/{filename}"}

@app.get("/result/{filename}")
def get_result(filename: str):
    file_path = os.path.join("backend/outputs", filename)
    print(f"file_path : {file_path}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(file_path, media_type="image/png")

### 검색 API 

#  YOLO 모델 (커스텀 모델이면 경로 교체)
model = YOLO("yolo11n.pt")  # 커스텀 학습한 요소/계절 모델 사용 가능 

# base64 이미지 입력 모델
class ImageRequest(BaseModel):
    image_base64: str

@app.post("/detect/")
def detect_objects(req: ImageRequest):
    try:
        # base64 → OpenCV 이미지 디코딩
        image_data = base64.b64decode(req.image_base64)
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # YOLO 추론
        results = model(img)
        labels = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls)
                label = model.names[cls_id]
                labels.append(label)

        # 요소/계절 태깅 로직 (예시)
        season_keywords = ["snow", "tree", "sun", "leaf", "flower"]
        season = classify_season(labels)

        return {"labels": labels, "season": season}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def classify_season(labels: List[str]) -> str:
    # 단순 규칙 기반 계절 추론 예시
    if "snow" in labels:
        return "winter"
    elif "leaf" in labels or "tree" in labels:
        return "autumn"
    elif "sun" in labels:
        return "summer"
    elif "flower" in labels:
        return "spring"
    else:
        return "unknown"



@app.post("/detect_season_vision/")
async def detect_season_vision(file: UploadFile = File(...)):
    try:
        #  파일 읽기
        print(file)
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # prompt = "What season is shown in this image? Please describe the scene in Korean and mention the season clearly."
        prompt = "What season is shown in this image? Please describe the scene in Korean and clearly mention any possible seasons."


        body = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ],
            "max_tokens": 300
        }

        async with httpx.AsyncClient() as client:
            res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        
        content = res.json()["choices"][0]["message"]["content"]
        print("🧠 GPT 응답:", content)

        # ✅ 계절 후보 리스트 추출
        matched_seasons = [season for season in season_enum if season in content]

        if matched_seasons:
            return {
                "season_candidates": matched_seasons,
                "reason": content,
                "SubCategoryList": [season_enum[s] for s in matched_seasons]
            }

        return {
            "season_candidates": ["unknown"],
            "reason": content,
            "SubCategoryList": []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class MapGenRequest(BaseModel):
    prompt: str

@app.post("/generate_map")
def generate_map_from_prompt(data: MapGenRequest):
    try:
        params = parse_prompt(data.prompt)
        generator = MapGenerator(**params)
        json_data = generator.generate_json()

        output_dir = "backend/outputs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"map_{uuid4().hex[:8]}.json"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, "w") as f:
            f.write(json_data)

        return {
            "json_path": f"/result/{filename}",
            "used_parameters": params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# class MapGenFullRequest(BaseModel):
#     prompt: str

# @app.post("/generate_map_full")
# def generate_map_full(data: MapGenFullRequest):
#     try:
#         # 1. LLM을 통해 섹션 리스트 생성 및 전체 맵 구성
#         generator = MapGenerator()
#         blocks = generator.generate_from_description(data.prompt)
#         json_data = json.dumps({"saveDataArray": blocks}, indent=2)

#         # 2. 저장 디렉토리
#         output_dir = "backend/outputs"
#         os.makedirs(output_dir, exist_ok=True)
#         filename = f"map_{uuid4().hex[:8]}"
#         json_path = os.path.join(output_dir, f"{filename}.json")

#         # 3. JSON 저장
#         with open(json_path, "w") as f:
#             f.write(json_data)

#         # 4. 이미지 시각화
#         xs, ys, zs = [], [], []
#         for block in blocks:
#             pos = block["position"]
#             xs.append(pos["x"])
#             ys.append(pos["y"])
#             zs.append(pos["z"])

#         fig = plt.figure()
#         ax = fig.add_subplot(111, projection='3d')
#         ax.scatter(xs, ys, zs, s=5)
#         ax.set_axis_off()
#         preview_path = os.path.join(output_dir, f"{filename}.png")
#         plt.savefig(preview_path)
#         plt.close()

#         return {
#             "json_path": f"/result/{filename}.json",
#             "preview_image": f"/result/{filename}.png",
#             "used_prompt": data.prompt
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

class MapGenSectionRequest(BaseModel):
    sections: list

@app.post("/generate_map_sections")
def generate_map_from_sections(data: MapGenSectionRequest):
    try:
        parser = ObjectParser("./pipeline/map_gen/object_metadata.json")
        generator = MapGenerator()
        result = generator.generate_from_sections(data.sections, parser)
        
        # 저장
        output_dir = "backend/outputs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"map_{uuid4().hex[:8]}"
        json_path = os.path.join(output_dir, f"{filename}.json")
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)

        # 이미지 저장
        xs, ys, zs = [], [], []
        for block in result["saveDataArray"]:
            xs.append(block["position"]["x"])
            ys.append(block["position"]["y"])
            zs.append(block["position"]["z"])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs, s=5)
        ax.set_axis_off()
        preview_path = os.path.join(output_dir, f"{filename}.png")
        plt.savefig(preview_path)
        plt.close()

        return {
            "json_path": f"/result/{filename}.json",
            "preview_image": f"/result/{filename}.png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))