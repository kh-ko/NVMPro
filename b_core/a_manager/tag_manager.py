import json
from PySide6.QtCore import QFile, QIODevice
from b_core.d_model.tag_model import TagModel
from b_core.d_model.combo_box_tag_model import ComboBoxTagModel

# 1. 폴더 구조를 담기 위한 데이터 클래스
class TagFolder:
    def __init__(self, name: str):
        self.name = name
        # 하위 폴더들 (이름을 Key로 가짐)
        self.folders: dict[str, 'TagFolder'] = {}
        # 이 폴더에 속한 태그들 (이름을 Key로 가짐)
        self.tags: dict[str, TagModel] = {}

class TagManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        """데이터 초기화를 담당하는 내부 메서드"""
        # 최상위 루트 폴더
        self.root_folder = TagFolder("Root")
        
        # 빠른 검색을 위한 평면(Flat) 딕셔너리 
        # Key: "폴더명/태그명" (예: "Connection/Valve_01")
        self._flat_tags: dict[str, TagModel] = {}

    def load_from_json(self, file_path: str) -> None:
        """Qt 리소스에서 JSON을 읽어 폴더/태그 구조를 구성합니다."""
        qfile = QFile(file_path)
        if not qfile.open(QIODevice.OpenModeFlag.ReadOnly):
            raise FileNotFoundError(f"Qt 리소스 파일을 열 수 없습니다: {file_path}")

        try:
            byte_data = qfile.readAll()
            json_text = byte_data.data().decode('utf-8')
            raw_data = json.loads(json_text)
        finally:
            qfile.close()

        # 기존 데이터 초기화
        self._init_manager()

        # 재귀적 파싱 시작 (최상위 raw_data를 루트 폴더에 매핑)
        self._parse_node(raw_data, self.root_folder, current_path="")

    def _parse_node(self, node_data: dict, current_folder: TagFolder, current_path: str) -> None:
        """폴더와 태그를 재귀적으로 파싱하는 내부 로직"""
        
        # 1. 현재 노드의 태그들 파싱
        for tag_data in node_data.get("Tags", []):
            tag_name = tag_data.get("Name")
            if not tag_name:
                continue

            component_type = tag_data.get("DefaultComponent", "")
            
            try:
                # 팩토리 로직
                if component_type == "ComboBox":
                    tag_obj = ComboBoxTagModel(**tag_data)
                else:
                    tag_obj = TagModel(**tag_data)

                # 폴더 객체에 태그 추가
                current_folder.tags[tag_name] = tag_obj

                # 빠른 검색용 Flat 딕셔너리에 추가 (경로 조합)
                full_path = f"{current_path}/{tag_name}" if current_path else tag_name
                self._flat_tags[full_path] = tag_obj

            except Exception as e:
                print(f"[{tag_name}] 태그 객체 생성 중 오류: {e}")

        # 2. 현재 노드의 하위 폴더들 파싱 (재귀 호출)
        for folder_data in node_data.get("Folders", []):
            folder_name = folder_data.get("Name")
            if not folder_name:
                continue

            # 새 폴더 객체 생성 및 연결
            new_folder = TagFolder(folder_name)
            current_folder.folders[folder_name] = new_folder

            # 하위 경로 생성 (예: "Connection" -> "Connection/SubFolder")
            new_path = f"{current_path}/{folder_name}" if current_path else folder_name
            
            # 자기 자신을 다시 호출하여 깊이 들어감
            self._parse_node(folder_data, new_folder, new_path)

    # --- 유틸리티 메서드 ---

    def get_tag(self, path: str) -> TagModel | None:
        """
        절대 경로를 사용하여 태그를 `O(1)` 속도로 반환합니다.
        예: manager.get_tag("Connection/Valve_01")
        """
        return self._flat_tags.get(path)

    def get_folder(self, path: str) -> TagFolder | None:
        """
        특정 경로의 폴더 객체를 반환합니다.
        예: manager.get_folder("Connection/MotorGroup")
        """
        if not path or path == "Root":
            return self.root_folder

        current = self.root_folder
        parts = path.split("/")
        
        for part in parts:
            if part in current.folders:
                current = current.folders[part]
            else:
                return None
        return current

    @property
    def total_tag_count(self) -> int:
        return len(self._flat_tags)

    def print_tree(self) -> None:
        """
        루트 폴더부터 시작하여 전체 태그 트리 구조와 세부 속성을 콘솔에 출력합니다.
        """
        print("\n======================= [ Tag Tree & Details ] =======================")
        print(f"📁 {self.root_folder.name}")
        self._print_tree_recursive(self.root_folder, level=1)
        print("======================================================================\n")

    def _print_tree_recursive(self, folder: 'TagFolder', level: int) -> None:
        indent = "    " * level
        detail_indent = "    " * (level + 1)
        
        # 1. 하위 폴더 출력
        for sub_folder_name, sub_folder in folder.folders.items():
            print(f"{indent}📁 {sub_folder_name}/")
            self._print_tree_recursive(sub_folder, level + 1)
            
        # 2. 현재 폴더의 태그 및 세부 속성 출력
        for tag_name, tag_obj in folder.tags.items():
            print(f"{indent}📄 {tag_name}")
            
            # Pydantic V2의 model_dump()를 사용하여 태그의 모든 속성을 딕셔너리로 추출
            tag_data = tag_obj.model_dump()
            keys = list(tag_data.keys())
            
            for i, key in enumerate(keys):
                val = tag_data[key]
                is_last = (i == len(keys) - 1)
                branch = "└─" if is_last else "├─"
                
                # ComboBox의 Options 속성일 경우 리스트 내부까지 예쁘게 전개해서 출력
                if key == "Options" and isinstance(val, list):
                    print(f"{detail_indent}{branch} {key}:")
                    for j, opt in enumerate(val):
                        opt_branch = "└─" if j == len(val) - 1 else "├─"
                        # opt는 딕셔너리 형태 {'Label': 'Auto', 'Value': 1}
                        print(f"{detail_indent}    {opt_branch} Label: '{opt['Label']}', Value: {opt['Value']}")
                else:
                    # 일반 속성 출력 (예: ├─ DataType: Base10)
                    print(f"{detail_indent}{branch} {key}: {val}")