from diffusers import StableDiffusionPipeline
import torch

def load_lora_pipeline(base_model='runwayml/stable-diffusion-v1-5', lora_path=None):
    pipe = StableDiffusionPipeline.from_pretrained(
        base_model,
        torch_dtype=torch.float16
    ).to('cuda')

    if lora_path:
        pipe.load_lora_weights(lora_path)
    return pipe
