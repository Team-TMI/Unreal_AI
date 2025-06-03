import json
import os
from glob import glob

def summarize_single_map(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    positions = [d["position"] for d in data.get("saveDataArray", []) if "position" in d]
    if not positions:
        return None

    xs = [p["x"] for p in positions]
    ys = [p["y"] for p in positions]
    zs = [p["z"] for p in positions]

    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    span_desc = []
    if dx > dy and dx > dz:
        span_desc.append("x축 직선 구조")
    if dy > dx and dy > dz:
        span_desc.append("y축 분기 구조")
    if dz > dx and dz > dy:
        span_desc.append("z축 상승 구조")

    z_jumps = sum(1 for i in range(1, len(zs)) if abs(zs[i] - zs[i - 1]) > 200)
    jump_desc = "점프 요소 있음" if z_jumps >= 2 else "점프 요소 적음"

    summary = f"""[맵 이름] {os.path.basename(file_path)}
                - 블록 수: {len(positions)}
                - 주요 구조: {", ".join(span_desc) if span_desc else "구조 파악 어려움"}
                - {jump_desc}
                """
    return summary

def summarize_map_folder(folder_path):
    files = sorted(glob(os.path.join(folder_path, "*.json")))
    summaries = [summarize_single_map(f) for f in files]
    return "\n".join([s for s in summaries if s])

# 요약 실행
summarized_text = summarize_map_folder("/mnt/data")
print(summarized_text[:1000])  # 앞부분만 확인
