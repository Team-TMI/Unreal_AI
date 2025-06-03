
import math
import json
import os
from pipeline.map_gen.object_loader import ObjectLoader
from pipeline.map_gen.prompt_assembler import assemble_prompt
from pipeline.map_gen.llm_caller import call_llm

class MapGenerator:
    def __init__(self, object_name, **kwargs):
        self.rotation = {"pitch": 0, "yaw": 0, "roll": 0}
        self.size = {"x": 12, "y": 20, "z": 5}
        self.used_positions = set()

        self.center_x = kwargs.get("center_x", 5000)
        self.center_y = kwargs.get("center_y", 500)
        self.base_z = kwargs.get("base_z", 100)
        self.params = kwargs

        base_dir = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, "object_list.csv")
        self.object_loader = ObjectLoader(csv_path)

        self.block_id = self.object_loader.get_id_by_name(object_name)

    def add_block(self, x, y, z):
        pos = (x, y, z)
        if pos in self.used_positions:
            return None
        self.used_positions.add(pos)
        return {
            "id": self.block_id,
            "position": {"x": x, "y": y, "z": z},
            "rotation": self.rotation,
            "size": self.size
        }

    def llm_parse_sections(self, user_description: str, reference_folder: str = "map_reference"):
        prompt = assemble_prompt(user_description, reference_folder)
        print("📨 LLM Prompt Preview:\n", prompt[:1000])

        raw = call_llm(prompt)
        try:
            sections = json.loads(raw)
            return sections
        except Exception as e:
            print("❌ LLM 응답 파싱 실패:", e)
            return []

    def generate_from_description(self, user_text: str):
        sections = self.llm_parse_sections(user_text)
        all_blocks = []

        current_x, current_y, current_z = self.center_x, self.center_y, self.base_z

        for section in sections:
            object_name = section.get("object", "술통")
            self.block_id = self.object_loader.get_id_by_name(object_name)

            if "start" not in section:
                section["start"] = {
                    "x": current_x,
                    "y": current_y,
                    "z": current_z
                }

            blocks = self.generate_section(section)
            all_blocks.extend(blocks)

            if blocks:
                last_pos = blocks[-1]["position"]
                current_x, current_y, current_z = last_pos["x"], last_pos["y"], last_pos["z"]

        return all_blocks

    def generate_section(self, section):
        t = section["type"]
        if t == "straight":
            return self.generate_straight(section)
        elif t == "split":
            return self.generate_split(section)
        elif t == "merge":
            return self.generate_merge(section)
        elif t == "jump":
            return self.generate_jump(section)
        elif t == "spiral":
            return self.generate_spiral(section)
        else:
            return []

    def generate_straight(self, section):
        blocks = []
        x, y, z = section["start"].values()
        dx = 100 if "x" in section["direction"] else 0
        dy = 100 if "y" in section["direction"] else 0
        for i in range(section["length"]):
            block = self.add_block(x + i * dx, y + i * dy, z)
            if block:
                blocks.append(block)
        return blocks

    def generate_split(self, section):
        blocks = []
        x, y, z = section["start"].values()
        dy = 100
        for i in range(section["length"]):
            block1 = self.add_block(x, y + i * dy, z)
            block2 = self.add_block(x, y - i * dy, z)
            if block1:
                blocks.append(block1)
            if block2:
                blocks.append(block2)
        return blocks

    def generate_merge(self, section):
        blocks = []
        x, y, z = section["start"].values()
        for i in range(section["length"]):
            block = self.add_block(x + i * 100, y, z)
            if block:
                blocks.append(block)
        return blocks

    def generate_jump(self, section):
        blocks = []
        x, y, z = section["start"].values()
        dx = 200 if "x" in section["direction"] else 0
        dy = 200 if "y" in section["direction"] else 0
        for i in range(section["length"]):
            block = self.add_block(x + i * dx, y + i * dy, z)
            if block:
                blocks.append(block)
        return blocks

    def generate_spiral(self, section):
        blocks = []
        turns = section.get("turns", 3)
        steps_per_turn = section.get("steps_per_turn", 12)
        radius = section.get("radius", 2500)
        z_step = section.get("z_step", 300)
        x0, y0, z0 = section["start"].values()

        angle_step = 360 / steps_per_turn
        total_steps = turns * steps_per_turn

        for step in range(total_steps):
            angle_deg = step * angle_step
            angle_rad = math.radians(angle_deg)
            x = x0 + int(radius * math.cos(angle_rad))
            y = y0 + int(radius * math.sin(angle_rad))
            z = z0 + step * z_step // steps_per_turn
            block = self.add_block(x, y, z)
            if block:
                blocks.append(block)
        return blocks
