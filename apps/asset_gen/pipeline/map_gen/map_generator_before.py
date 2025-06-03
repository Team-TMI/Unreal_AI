import math

class MapGenerator:
    def __init__(self):
        self.used_positions = set()
        self.current_position = {"x": 4900, "y": 500, "z": -150}  # 시작 좌표 고정

    # def place_block(self, prop, x, y, z):
    #     # return {"x": x, "y": y, "z": z, "prop": prop}
    #     return {
    #         "position": {"x": x, "y": y, "z": z},
    #         "prop": prop
    #     }

    def place_block(self, object_id, x, y, z):
        return {
            "iD": str(object_id),
            "position": {
                "x": x,
                "y": y,
                "z": z
            },
            "rotation": {
                "pitch": 0,
                "yaw": 0,
                "roll": 0
            },
            "size": {
                "x": 1,
                "y": 1,
                "z": 1
            }
        }

    # def generate_block(self, section):
    #     width = section.get("width", 1)
    #     depth = section.get("depth", 1)
    #     height = section.get("height", 1)
    #     object_ids = section.get("object", ["땅1"])

    #     x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]
    #     blocks = []

    #     for h in range(height):
    #         for i in range(width):
    #             for j in range(depth):
    #                 px = x + i * 100
    #                 py = y + j * 100
    #                 pz = z + h * 100
    #                 pos = (px, py, pz)
    #                 if pos in self.used_positions:
    #                     continue
    #                 self.used_positions.add(pos)
    #                 blocks.append(self.place_block(object_ids[0], px, py, pz))

    #     print(f"placing {object_ids[0]} at ({px}, {py}, {pz})")
    #     print(f"Total blocks generated: {len(blocks)}")

    #     # 현재 위치 업데이트: 마지막 블록의 꼭대기 중앙
    #     self.current_position = {
    #         "x": x,
    #         "y": y,
    #         "z": z + height * 100 + 100 
    #     }
    #     return blocks
    def generate_block(self, section):
        width = section.get("width", 1)
        depth = section.get("depth", 1)
        height = section.get("height", 1)
        object_ids = section.get("object_ids", [0])  # 이미 resolve_object_ids에서 ID로 변환되어 있음

        x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]
        blocks = []
        idx = 0

        for h in range(height):
            for i in range(width):
                for j in range(depth):
                    px = x + i * 100
                    py = y + j * 100
                    pz = z + h * 100
                    pos = (px, py, pz)
                    if pos in self.used_positions:
                        continue
                    self.used_positions.add(pos)
                    blocks.append(self.place_block(object_ids[idx % len(object_ids)], px, py, pz))
                    idx += 1

        self.current_position = {
            "x": x,
            "y": y,
            "z": z + height * 100 + 100 
        }
        return blocks

    
    def generate_from_sections(self, sections, parser):
        all_blocks = []
        for section in sections:
            self.resolve_object_ids(section, parser)
            blocks = self.generate_section(section)
            all_blocks.extend(blocks)
        return {"saveDataArray": all_blocks}

    # def resolve_object_ids(self, section, parser):
    #     names = section.get("object", [])
    #     ids = [parser.get_id_by_name(name) for name in names]
    #     section["object_ids"] = ids
    #     return section

    def resolve_object_ids(self, section, parser):
        print(f"🧩 section: {section}")
        names = section.get("object", [])
        if not names:
            raise ValueError(f"🛑 'object' key missing or empty in section: {section}")
        ids = [parser.get_id_by_name(name) for name in names]
        if not all(ids):
            raise ValueError(f"🛑 Failed to resolve object_ids for names: {names}")
        section["object_ids"] = ids


    def generate_line(self, section):
        start = section.get("start", {"x": 0, "y": 0, "z": 100})
        direction = section.get("direction", "z")
        length = section.get("length", 10)
        unit = section.get("unit", 100)
        object_ids = section.get("object_ids", [])

        # x, y, z = start["x"], start["y"], start["z"]
        x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]

        blocks, idx = [], 0

        for i in range(length):
            if direction == "x": pos = (x + i * unit, y, z)
            elif direction == "y": pos = (x, y + i * unit, z)
            else: pos = (x, y, z + i * unit)
            if pos in self.used_positions: continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[idx % len(object_ids)], *pos))
            idx += 1
        return blocks

    def generate_cylinder(self, section):
        cx, cy = self.current_position["x"], self.current_position["y"]
        inner_r = section.get("inner_radius", 1300)
        outer_r = section.get("outer_radius", 1500)
        height = section.get("height", 4000)
        unit = section.get("unit", 100)
        object_ids = section.get("object", ["땅1"])

        blocks, idx = [], 0
        for z in range(100, height + 1, unit):
            for x in range(-outer_r, outer_r + 1, unit):
                for y in range(-outer_r, outer_r + 1, unit):
                    r = math.sqrt(x ** 2 + y ** 2)
                    if inner_r <= r <= outer_r:
                        px, py, pz = cx + x, cy + y, self.current_position["z"] + z
                        pos = (px, py, pz)
                        if pos in self.used_positions:
                            continue
                        self.used_positions.add(pos)
                        blocks.append(self.place_block(object_ids[idx % len(object_ids)], px, py, pz))
                        idx += 1

        self.current_position["z"] += height + 100
        return blocks

    def generate_spiral(self, section):
        cx, cy = self.current_position["x"], self.current_position["y"]
        turns = section.get("turns", 3)
        steps = section.get("steps_per_turn", 12)
        radius = section.get("radius", 2500)
        z_step = section.get("z_step", 300)
        object_ids = section.get("object", ["땅1"])

        angle_step = 360 / steps
        blocks, idx = [], 0

        for step in range(turns * steps):
            a = math.radians(step * angle_step)
            x = cx + int(radius * math.cos(a))
            y = cy + int(radius * math.sin(a))
            z = self.current_position["z"] + step * z_step // steps
            pos = (x, y, z)
            if pos in self.used_positions:
                continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[idx % len(object_ids)], x, y, z))
            idx += 1

        self.current_position["z"] += z_step + 100
        return blocks

    def generate_zigzag(self, section):
        start = section.get("start", {"x": 0, "y": 0, "z": 100})
        direction = section.get("direction", "x")
        length, unit, amp = section.get("length", 10), section.get("unit", 100), section.get("amplitude", 1)
        object_ids = section.get("object_ids", [])

        # x, y, z = start["x"], start["y"], start["z"]
        x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]

        
        blocks, idx = [], 0

        for i in range(length):
            if direction == "x":
                px, py, pz = x + i * unit, y + ((-1)**i) * amp * unit, z
            elif direction == "y":
                px, py, pz = x + ((-1)**i) * amp * unit, y + i * unit, z
            else:
                px, py, pz = x, y + ((-1)**i) * amp * unit, z + i * unit
            pos = (px, py, pz)
            if pos in self.used_positions: continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[idx % len(object_ids)], px, py, pz))
            idx += 1
        return blocks

    def generate_step(self, section):
        start = section.get("start", {"x": 0, "y": 0, "z": 100})
        direction = section.get("direction", "x")
        length, unit, rise = section.get("length", 10), section.get("unit", 100), section.get("rise", 100)
        object_ids = section.get("object_ids", [])

        x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]
        blocks, idx = [], 0

        for i in range(length):
            if direction == "x": px, py = x + i * unit, y
            else: px, py = x, y + i * unit
            pz = z + i * rise
            pos = (px, py, pz)
            if pos in self.used_positions: continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[idx % len(object_ids)], px, py, pz))
            idx += 1
        return blocks

    # def generate_stair(self, section):
    #     steps = section.get("steps", 5)
    #     z_step = section.get("z_step", 100)
    #     unit = section.get("unit", 100)
    #     object_ids = section.get("object", ["나무상자"])

    #     x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]
    #     blocks = []
    #     for i in range(steps):
    #         px = x + i * unit
    #         py = y
    #         pz = z + i * z_step
    #         pos = (px, py, pz)
    #         if pos in self.used_positions:
    #             continue
    #         self.used_positions.add(pos)
    #         blocks.append(self.place_block(object_ids[0], px, py, pz))

    #     # stair 끝 점을 다음 시작 좌표로 저장
    #     self.current_position = {"x": px, "y": py, "z": pz + 100}
    #     return blocks

    def generate_stair(self, section):
        steps = section.get("steps", 5)
        z_step = section.get("z_step", 100)
        unit = section.get("unit", 100)
        object_ids = section.get("object", ["나무상자"])

        x, y, z = self.current_position["x"], self.current_position["y"], self.current_position["z"]
        blocks = []
        for i in range(steps):
            px = x + i * unit
            py = y
            pz = z + i * z_step
            pos = (px, py, pz)
            if pos in self.used_positions:
                continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[0], px, py, pz))

        self.current_position = {
            "x": x + (steps - 1) * unit,
            "y": y,
            "z": z + (steps - 1) * z_step + 100
        }
        return blocks

    def generate_section(self, section):
        pattern_map = {
            "square": self.generate_block,
            "block": self.generate_block,
            "line": self.generate_line,
            "cylinder": self.generate_cylinder,
            "spiral": self.generate_spiral,
            "zigzag": self.generate_zigzag,
            "step": self.generate_step,
            "stair": self.generate_stair
        }
        # pattern = section.get("pattern", "block")
        # generator = pattern_map.get(pattern)
        # return generator(section) if generator else []
        pattern = section.get("pattern")
        if not pattern:
            raise ValueError(f"🛑 'pattern' key missing in section: {section}")
        
        generator = pattern_map.get(pattern)
        if generator is None:
            raise ValueError(f"🛑 Unknown pattern '{pattern}' in section: {section}")
        
        return generator(section)
