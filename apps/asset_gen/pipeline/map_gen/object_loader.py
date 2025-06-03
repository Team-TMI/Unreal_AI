import pandas as pd
import re

class ObjectLoader:
    def __init__(self, csv_path):
        self.data = self._load(csv_path)
        self.name_to_id = {
            self._extract_korean_name(obj["PropName"]): obj["PropID"]
            for obj in self.data
        }

    def _load(self, path):
        df = pd.read_csv(path, encoding="utf-8-sig")
        return df.to_dict(orient="records")

    def _extract_korean_name(self, propname):
        try:
            match = re.search(r'"([^"]+)"\s*\)?$', propname.strip())
            return match.group(1) if match else propname.strip()
        except Exception:
            return propname.strip()

    def get_id_by_name(self, name: str) -> str:
        return self.name_to_id.get(name.strip(), "1014")  # fallback: 골인지점 블록 ID
