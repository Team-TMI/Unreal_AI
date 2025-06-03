

from pipeline.map_gen.map_generator import MapGenerator

def parse_prompt(prompt: str):
    prompt = prompt.lower()

    if "나선" in prompt:
        return {
            "type": "spiral",
            "params": {
                "turns": 4 if "4" in prompt else 3,
                "steps_per_turn": 16 if "촘촘" in prompt else 12,
                "stair_radius": 2000 if "좁" in prompt or "촘촘" in prompt else 2500
            }
        }
    elif "8자" in prompt or "8자 모양" in prompt:
        return {
            "type": "figure8",
            "params": {
                "loops": 2,
                "step_interval": 3,
                "z_increment": 500,
                "radius": 2000
            }
        }
    elif "지그재그" in prompt or "지그" in prompt:
        return {
            "type": "zigzag",
            "params": {
                "width": 3000,
                "length": 8000,
                "segment_length": 600,
                "z_step": 500
            }
        }
    elif "다리" in prompt or "bridge" in prompt:
        return {
            "type": "bridge",
            "params": {
                "length": 10000,
                "width": 1000,
                "height": 100
            }
        }
    elif "미로" in prompt or "maze" in prompt:
        return {
            "type": "maze",
            "params": {
                "grid_size": 10,
                "cell_size": 500,
                "wall_height": 1000
            }
        }
    else:
        return {
            "type": "spiral",
            "params": {
                "turns": 3,
                "steps_per_turn": 12,
                "stair_radius": 2500
            }
        }

if __name__ == "__main__":
    rule = parse_prompt("8자 모양 계단을 만들어줘")
    gen = MapGenerator(**rule["params"])
    json_data = gen.generate_json(rule["type"])
    with open("test_output.json", "w") as f:
        f.write(json_data)
    print("✅ 생성 완료 →", rule["type"], rule["params"])