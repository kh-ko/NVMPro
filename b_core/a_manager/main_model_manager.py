from b_core.a_manager.tag_manager import TagManager
from b_core.e_define.file_folder_define import TAG_SCHEMA_FILE

class MainModelManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.tag_manager = TagManager()
        self.tag_manager.load_from_json(TAG_SCHEMA_FILE)

        # 디버깅용 : self.tag_manager.print_tree()