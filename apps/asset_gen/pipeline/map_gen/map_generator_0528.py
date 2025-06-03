
import math

class MapGenerator:
    def __init__(self, used_positions=None):
        self.used_positions = used_positions if used_positions is not None else set()

    def place_block(self, obj_id, x, y, z, size=1):
        return {
            "id": obj_id,
            "position": {"x": x, "y": y, "z": z},
            "rotation": {"pitch": 0, "yaw": 0, "roll": 0},
            "size": {"x": size, "y": size, "z": size}
        }
    
    def generate_from_sections(self, sections, parser):
        all_blocks = []
        for section in sections:
            self.resolve_object_ids(section, parser)
            blocks = self.generate_section(section)
            all_blocks.extend(blocks)
        return {"saveDataArray": all_blocks}

    # def generate_section(self, section):
    #     type_map = {
    #         "block": self.generate_block,
    #         "line": self.generate_line,
    #         "cylinder": self.generate_cylinder,
    #         "spiral": self.generate_spiral,
    #         "zigzag": self.generate_zigzag,
    #         "step": self.generate_step
    #     }
    #     gen_func = type_map.get(section["type"])
    #     return gen_func(section) if gen_func else []
    
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
        pattern = section.get("pattern", "block")
        generator = pattern_map.get(pattern)
        return generator(section) if generator else []
    
    def resolve_object_ids(self, section, parser):
        names = section.get("object", [])
        ids = [parser.get_id_by_name(name) for name in names]
        section["object_ids"] = ids
        return section

    def generate_block(self, section):
        cx = section.get("center", {}).get("x", 0)
        cy = section.get("center", {}).get("y", 0)
        width = section.get("width", 3)
        depth = section.get("depth", 3)
        height = section.get("height", 1)
        unit = section.get("unit", 100)
        object_ids = section.get("object_ids", [])

        blocks, idx = [], 0
        start_x = cx - (width // 2) * unit
        start_y = cy - (depth // 2) * unit

        for h in range(height):
            z = 100 + h * unit
            for i in range(width):
                for j in range(depth):
                    x, y = start_x + i * unit, start_y + j * unit
                    pos = (x, y, z)
                    if pos in self.used_positions: continue
                    self.used_positions.add(pos)
                    blocks.append(self.place_block(object_ids[idx % len(object_ids)], x, y, z))
                    idx += 1
        return blocks

    def generate_line(self, section):
        start = section.get("start", {"x": 0, "y": 0, "z": 100})
        direction = section.get("direction", "z")
        length = section.get("length", 10)
        unit = section.get("unit", 100)
        object_ids = section.get("object_ids", [])

        x, y, z = start["x"], start["y"], start["z"]
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
        cx = section.get("center", {}).get("x", 0)
        cy = section.get("center", {}).get("y", 0)
        inner_r, outer_r = section.get("inner_radius", 1300), section.get("outer_radius", 1500)
        height, unit = section.get("height", 4000), section.get("unit", 100)
        object_ids = section.get("object_ids", [])

        blocks, idx = [], 0
        for z in range(100, height + 1, unit):
            for x in range(-outer_r, outer_r + 1, unit):
                for y in range(-outer_r, outer_r + 1, unit):
                    r = math.sqrt(x**2 + y**2)
                    if inner_r <= r <= outer_r:
                        px, py, pz = cx + x, cy + y, z
                        pos = (px, py, pz)
                        if pos in self.used_positions: continue
                        self.used_positions.add(pos)
                        blocks.append(self.place_block(object_ids[idx % len(object_ids)], px, py, pz))
                        idx += 1
        return blocks

    def generate_spiral(self, section):
        cx, cy = section.get("center", {}).get("x", 0), section.get("center", {}).get("y", 0)
        turns, steps, radius, z_step = section.get("turns", 3), section.get("steps_per_turn", 12), section.get("radius", 2500), section.get("z_step", 300)
        object_ids = section.get("object_ids", [])
        angle_step = 360 / steps
        blocks, idx = [], 0

        for step in range(turns * steps):
            a = math.radians(step * angle_step)
            x, y = cx + int(radius * math.cos(a)), cy + int(radius * math.sin(a))
            z = 100 + step * z_step // steps
            pos = (x, y, z)
            if pos in self.used_positions: continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[idx % len(object_ids)], x, y, z))
            idx += 1
        return blocks

    def generate_zigzag(self, section):
        start = section.get("start", {"x": 0, "y": 0, "z": 100})
        direction = section.get("direction", "x")
        length, unit, amp = section.get("length", 10), section.get("unit", 100), section.get("amplitude", 1)
        object_ids = section.get("object_ids", [])

        x, y, z = start["x"], start["y"], start["z"]
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

        x, y, z = start["x"], start["y"], start["z"]
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

    def generate_stair(self, section):
        start = section.get("start", {"x": 4900, "y": 500, "z": -150})
        steps = section.get("steps", 5)
        z_step = section.get("z_step", 100)
        unit = section.get("unit", 100)
        object_ids = section.get("object_ids", [])

        x, y, z = start["x"], start["y"], start["z"]
        blocks, idx = [], 0

        for i in range(steps):
            px = x + i * unit
            py = y
            pz = z + i * z_step
            pos = (px, py, pz)
            if pos in self.used_positions: continue
            self.used_positions.add(pos)
            blocks.append(self.place_block(object_ids[idx % len(object_ids)], px, py, pz))
            idx += 1

        return blocks

