
import json
import re

class ObjectParser:
    def __init__(self, metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.object_map = json.load(f)
        self.all_names = list(self.object_map.keys())

    def extract_candidates(self, prompt: str):
        candidates = []
        for name in self.all_names:
            if name in prompt:
                candidates.append({
                    "name": name,
                    **self.object_map[name]
                })
        return candidates if candidates else [self.get_fallback()]

    # def get_fallback(self):
    #     fallback = "수풀1" if "수풀1" in self.object_map else list(self.object_map.keys())[0]
    #     return {
    #         "name": fallback,
    #         **self.object_map[fallback]
    #     }
    
    def get_id_by_name(self, name: str) -> str:
        """한글 오브젝트 이름 → prop_id"""
        if name in self.object_map:
            return self.object_map[name]["prop_id"]
        return "1014"  # fallback id

    def best_match(self, prompt: str):
        # 가장 먼저 등장한 후보 하나만 반환
        candidates = self.extract_candidates(prompt)
        return candidates[0] if candidates else self.get_fallback()
