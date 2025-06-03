# frontend/app.py
import streamlit as st
import requests

st.set_page_config(page_title="Astralloom Texture Generator", layout="centered")
st.title("🧱 Astralloom Texture Generator ")

prompt = st.text_input("🎨 텍스처 설명을 입력하세요", "mossy stone wall")
seed = st.number_input("🎲 시드값 (일관성 유지용)", value=42, step=1)
mode = st.radio("🧪 생성 타입 선택", ["albedo", "normal"], index=0, horizontal=True)

if st.button("🚀 텍스처 생성 요청"):
    with st.spinner("백엔드에 텍스처 생성 요청 중..."):
        res = requests.post(
            "http://localhost:8000/generate_quadrant",
            json={"prompt": prompt, "seed": seed, "mode": mode}
        )

        if res.status_code == 200 and "image_path" in res.json():
            image_url = "http://localhost:8000" + res.json()["image_path"]
            st.success("✅ 생성 완료!")
            st.image(image_url, caption=f"🖼️ 생성된 {mode} 텍스처", use_container_width=True)
        else:
            st.error(f"❌ 오류 발생: {res.text}")
