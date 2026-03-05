from PySide6.QtWidgets import QVBoxLayout
from b_core.d_model.combo_box_tag_model import ComboBoxTagModel
from c_ui.b_components.a_custom.tag_combobox import TagComboBox
from c_ui.b_components.a_custom.tag_inputnumber import TagInputNumber

class TagComponentHelper:
    @staticmethod
    def build_tag_frame(tag_manager, folder_name: str):
        """
        TagManager에서 특정 폴더를 읽어 QVBoxLayout과 생성된 위젯 딕셔너리를 반환합니다.
        
        Args:
            tag_manager: 태그 정보를 관리하는 인스턴스
            folder_name (str): 가져올 폴더명 (예: "Connection")
            
        Returns:
            tuple: (QVBoxLayout, dict) - 레이아웃과 생성된 위젯들이 담긴 딕셔너리
        """
        v_layout = QVBoxLayout()
        v_layout.setSpacing(10)
        v_layout.setContentsMargins(0, 0, 0, 0)
        ui_widgets = {}

        folder = tag_manager.get_folder(folder_name)
        if not folder:
            print(f"[TagComponentHelper] Failed to load '{folder_name}' folder from TagManager.")
            return v_layout, ui_widgets

        # 폴더 안의 태그들을 순회하며 위젯 추가
        for tag_name, tag_obj in folder.tags.items():
            if not tag_obj.IsUsed:
                continue

            widget = None
            
            # ComboBox 타입일 경우
            if tag_obj.DefaultComponent == "ComboBox" or isinstance(tag_obj, ComboBoxTagModel):
                widget = TagComboBox(tag_obj)

            # InputNumber 타입일 경우
            elif tag_obj.DefaultComponent == "InputNumber":
                widget = TagInputNumber(tag_obj)

            # 그 외 기본 위젯 (현재는 InputNumber로 통일)
            else:
                widget = TagInputNumber(tag_obj)

            # 레이아웃에 추가 및 딕셔너리 저장
            if widget:
                widget.setObjectName(tag_name)
                v_layout.addWidget(widget)
                ui_widgets[tag_name] = widget

        # 모든 위젯을 위쪽으로 확실하게 밀어올리기 위해 빈 공간(Stretch) 추가
        v_layout.addStretch()

        return v_layout, ui_widgets