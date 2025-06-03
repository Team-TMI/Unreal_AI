from diffusers import StableDiffusionPipeline
import torch
from pathlib import Path
from uuid import uuid4
from PIL import Image

# 모델 로드 (최초 한 번만)
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe.to("cuda")
pipe.enable_attention_slicing()

output_dir = Path("img/generated")
output_dir.mkdir(parents=True, exist_ok=True)

def generate_image_from_prompt(prompt: str) -> str:
    image = pipe(prompt, num_inference_steps=30).images[0]
    filename = f"gen_{uuid4().hex[:8]}.png"
    output_path = output_dir / filename
    image.save(output_path)
    return str(output_path)
