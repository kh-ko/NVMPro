from PySide6.QtWidgets import QFormLayout, QComboBox, QLineEdit
from b_core.d_model.combo_box_tag_model import ComboBoxTagModel
from c_ui.b_components.a_custom.base_caption_label import BaseCaptionLabel

class TagComponentHelper:
    @staticmethod
    def build_tag_frame(tag_manager, folder_name: str):
        """
        TagManager에서 특정 폴더를 읽어 QFormLayout과 생성된 위젯 딕셔너리를 반환합니다.
        
        Args:
            tag_manager: 태그 정보를 관리하는 인스턴스
            folder_name (str): 가져올 폴더명 (예: "Connection")
            
        Returns:
            tuple: (QFormLayout, dict) - 폼 레이아웃과 생성된 위젯들이 담긴 딕셔너리
        """
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        ui_widgets = {}

        folder = tag_manager.get_folder(folder_name)
        if not folder:
            print(f"[TagComponentHelper] Failed to load '{folder_name}' folder from TagManager.")
            return form_layout, ui_widgets

        # 폴더 안의 태그들을 순회하며 위젯 추가
        for tag_name, tag_obj in folder.tags.items():
            if not tag_obj.IsUsed:
                continue

            widget = None
            
            # ComboBox 타입일 경우
            if tag_obj.DefaultComponent == "ComboBox" or isinstance(tag_obj, ComboBoxTagModel):
                combo = QComboBox()
                if isinstance(tag_obj, ComboBoxTagModel):
                    for option in tag_obj.Options:
                        combo.addItem(option.Label, option.Value)
                widget = combo

            # InputNumber 타입일 경우
            elif tag_obj.DefaultComponent == "InputNumber":
                widget = QLineEdit()
                # 필요시 QIntValidator 등 추가 가능

            # 그 외 기본 위젯
            else:
                widget = QLineEdit()

            # 레이아웃에 추가 및 딕셔너리 저장
            if widget:
                widget.setObjectName(tag_name)
                label = BaseCaptionLabel(tag_name)
                
                form_layout.addRow(label, widget)
                ui_widgets[tag_name] = widget

        return form_layout, ui_widgets    