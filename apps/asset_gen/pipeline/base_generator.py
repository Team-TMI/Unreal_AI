import torch
from PIL import Image
from diffusers import StableDiffusionPipeline

class BaseTextureGenerator:
    def __init__(self, mode="albedo"):
        if mode == "normal":
            model_id = "dream-texture/dreamtexture-sd15-normal"
        else:
            model_id = "runwayml/stable-diffusion-v1-5"
            
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16
        ).to("cuda")

    def apply_lora(self, lora_path):
        self.pipe.load_lora_weights(lora_path)

    def generate(self, prompt: str, output_path: str = "out.png"):
        image = self.pipe(prompt).images[0]
        image.save(output_path)
        return output_path
    
    def generate_quadrant_texture(self, base_prompt: str, output_path: str = "final_texture.png", seed: int = 42) -> str:
            """
            4개의 프롬프트로 텍스처를 생성하고 하나의 1024x1024 이미지로 합성한다.
            순서는 다음과 같다: top, variation1, variation2, side(seamless)
            
            Args:
                pipe: StableDiffusionPipeline 객체 (이미 LoRA 적용된 상태여도 됨)
                base_prompt: 텍스처의 주제 예: "mossy stone wall"
                output_path: 저장될 파일 경로
            
            Returns:
                최종 저장된 파일 경로 문자열
            """
            generator = torch.Generator(device="cuda").manual_seed(seed)

            if "normal" in self.pipe.config._name_or_path.lower():
                # DreamTexture용 프롬프트 구성
                prompts = [
                    f"top down normal texture of {base_prompt}, 8k, game asset style",
                    f"slight variation top down normal map of {base_prompt}, consistent style",
                    f"another normal view of {base_prompt}, variation in surface detail",
                    f"side view normal map of {base_prompt}, seamless pattern, 8k"
                ]
            else:
                # 기본 albedo 프롬프트
                prompts = [
                    f"smlstxtr,top view of {base_prompt}, tileable, pbr, consistent pattern, highly detailed, seamless texture for best results",
                    f"smlstxtr,slight variation of top view of {base_prompt}, same layout and texture type, seamless texture for best results",
                    f"smlstxtr,another slight top variation of {base_prompt}, minor changes only, seamless texture for best results",
                    f"smlstxtr,side view of {base_prompt}, same style, horizontal seamless tiling, pbr, seamless texture for best results"
                ]


            imgs = [self.pipe(p, generator=generator).images[0].resize((512, 512)) for p in prompts]

            canvas = Image.new("RGB", (1024, 1024))
            canvas.paste(imgs[0], (0, 0))
            canvas.paste(imgs[1], (512, 0))
            canvas.paste(imgs[2], (0, 512))
            canvas.paste(imgs[3], (512, 512))
            canvas.save(output_path)
            return output_path