import os
import streamlit as st
from pipeline.base_generator import BaseTextureGenerator

# PEFT backend 활성화
os.environ["DIFFUSERS_USE_PEFT_BACKEND"] = "1"

# LoRA 목록
lora_options = {
    "Flux Seamless Texture": "gokaygokay/Flux-Seamless-Texture-LoRA",
    "Another LoRA Texture": "lora_models/another_lora"
}

# UI
st.set_page_config(page_title="Astralloom Texture Generator", layout="centered")
st.title("🧱 Astralloom 4-Quadrant Texture Generator")

# 입력 UI
selected_lora = st.selectbox("🔧 사용할 LoRA 모델을 선택하세요", list(lora_options.keys()))
base_prompt = st.text_input("🎨 텍스처 주제 (자동 4프롬프트 생성됨, 영문작성 해주세요)", "mossy stone wall")

if st.button("🚀 4분할 텍스처 생성"):
    st.info(f"🔄 {selected_lora} 모델을 적용 중...")

    # 파이프라인 준비
    generator = BaseTextureGenerator()
    generator.apply_lora(lora_options[selected_lora])

    # 4프롬프트 → 4분할 생성
    output_path = generator.generate_quadrant_texture(base_prompt)
    
    st.success("✅ 4분할 텍스처 생성 완료!")
    st.image(output_path, caption="🧱 1024x1024 합성 텍스처", use_column_width=True)
