import json
from c_ui.b_components.b_composite.tag_widget import TagWidget

class JsonHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JsonHelper, cls).__new__(cls)
        return cls._instance

    def save_json(self, file_path, data):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"JSON 파일 저장 중 에러 발생: {e}")
            return False
        return True

    def load_json(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON 파일 로드 중 에러 발생: {e}")
            return None

