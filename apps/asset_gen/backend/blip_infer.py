from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import base64
import io
from PIL import Image

# 모델 불러오기
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", device_map="cuda", torch_dtype=torch.float16
)
model.eval()

def infer_season_from_image(base64_str: str) -> str:
    # 1. 이미지 디코딩
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 2. 영어 프롬프트
    prompt = "What season is shown in this image? Answer in Korean."

    # 3. Processor 입력
    inputs = processor(images=image, text=prompt, return_tensors="pt")

    # 4. 반드시 GPU로 이동!
    for k in inputs:
        inputs[k] = inputs[k].to("cuda")

    # 5. 생성
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=100)

    output = processor.decode(generated_ids[0], skip_special_tokens=True)
    return output
