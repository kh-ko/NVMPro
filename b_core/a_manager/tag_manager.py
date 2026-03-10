import json
from PySide6.QtCore import QFile, QIODevice
from b_core.d_model.tag_model import TagModel
# from b_core.d_model.combo_box_tag_model import ComboBoxTagModel  <- 더 이상 필요 없음 (TagModel에 완벽 통합됨)

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
        # Key: "Path/Name" (예: "Connection/BaudRate")
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

        # 평탄화된 배열 파싱 시작
        for tag_data in raw_data.get("Tags", []):
            tag_name = tag_data.get("Name")
            if not tag_name:
                continue
                
            path_str = tag_data.get("Path", "")

            try:
                # 1. 이전 단계에서 완성한 강력한 TagModel로 객체 생성 (분기 불필요)
                tag_obj = TagModel.model_validate(tag_data)

                # 2. Path 문자열을 분석하여 폴더 객체 가져오기 (없으면 자동 생성)
                target_folder = self._get_or_create_folder(path_str)

                # 3. 폴더 객체에 태그 추가
                target_folder.tags[tag_name] = tag_obj

                # 4. 빠른 검색용 Flat 딕셔너리에 추가 (경로 조합)
                full_path = f"{path_str}/{tag_name}" if path_str else tag_name
                self._flat_tags[full_path] = tag_obj

            except Exception as e:
                print(f"[{tag_name}] 태그 객체 생성 중 오류: {e}")

    def _get_or_create_folder(self, path: str) -> TagFolder:
        """
        주어진 경로(예: 'Connection/Network')에 해당하는 폴더 객체를 반환합니다.
        중간 경로 폴더가 없다면 자동으로 생성하여 트리를 구성합니다.
        """
        if not path:
            return self.root_folder
            
        current = self.root_folder
        parts = path.split("/")
        
        for part in parts:
            if part not in current.folders:
                current.folders[part] = TagFolder(part)
            current = current.folders[part]
            
        return current

    # --- 유틸리티 메서드 ---

    def get_tag(self, full_path: str) -> TagModel | None:
        """
        절대 경로를 사용하여 태그를 `O(1)` 속도로 반환합니다.
        예: manager.get_tag("Connection/BaudRate")
        """
        return self._flat_tags.get(full_path)

    def get_folder(self, path: str) -> TagFolder | None:
        """
        특정 경로의 폴더 객체를 반환합니다.
        예: manager.get_folder("Connection")
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

    def get_tags_in_folder(self, path: str) -> list[TagModel]:
        """
        특정 경로(폴더)에 직접 속해 있는 태그 객체들의 리스트를 반환합니다.
        경로가 잘못되었거나 태그가 없다면 빈 리스트를 반환합니다.
        예: manager.get_tags_in_folder("Connection")
        """
        folder = self.get_folder(path)
        
        if folder:
            # 딕셔너리의 value(TagModel 객체)들만 뽑아서 리스트로 변환하여 반환
            return list(folder.tags.values())
        
        return []

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
                if key == "Options" and isinstance(val, list) and len(val) > 0:
                    print(f"{detail_indent}{branch} {key}:")
                    for j, opt in enumerate(val):
                        opt_branch = "└─" if j == len(val) - 1 else "├─"
                        # 새로 추가하신 IsEnable 속성도 함께 출력되도록 반영
                        print(f"{detail_indent}    {opt_branch} Label: '{opt['Label']}', Value: {opt['Value']}, IsEnable: {opt.get('IsEnable', True)}")
                else:
                    print(f"{detail_indent}{branch} {key}: {val}")