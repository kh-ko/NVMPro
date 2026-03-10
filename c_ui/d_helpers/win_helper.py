from c_ui.b_components.b_composite.tag_widget import TagWidget

class WinHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WinHelper, cls).__new__(cls)
            cls._instance.windows = {}
        return cls._instance

    def show_window(self, win_class, *args, **kwargs):
        """
        win_class: 생성할 윈도우 클래스
        지정된 클래스의 창을 싱글톤으로 관리하여 띄웁니다.
        창이 파괴(닫힘)되면 관리 목록에서 자동으로 제거합니다.
        """
        win_name = win_class.__name__

        # 창이 이미 존재하면 앞으로 가져오기만 한다
        if win_name in self.windows:
            win = self.windows[win_name]
            win.show()
            win.raise_()
            win.activateWindow()
            return win

        # 창이 없으면 새로 생성
        new_win = win_class(*args, **kwargs)
        self.windows[win_name] = new_win

        # 창이 닫혀서 파괴될 때 딕셔너리에서 제거하도록 연결
        # QWidget의 destroyed 시그널을 이용 (WA_DeleteOnClose 속성이 있어야 함)
        new_win.destroyed.connect(lambda obj=None, name=win_name: self._on_window_destroyed(name))

        new_win.show()
        return new_win

    def _on_window_destroyed(self, win_name):
        """창이 소멸될 때 호출되어 관리 딕셔너리에서 삭제"""
        if win_name in self.windows:
            del self.windows[win_name]

    def build_tag_defalut_components(self, layout, tag_list: list):
        """태그 컴포넌트를 생성하고 레이아웃에 추가합니다. 생성된 TagWidget 리스트를 반환합니다."""
        created_widgets = []
        for tag in tag_list:
            tag_widget = TagWidget(tag_model=tag, component_type=tag.DefaultComponent)
            layout.addWidget(tag_widget)
            created_widgets.append(tag_widget)
        
        self.bind_widget_dependencies(created_widgets)
        return created_widgets

    def bind_widget_dependencies(self, tag_comp_list):
        # 1. 이름으로 대상을 빠르게 찾기 위해 컴포넌트 딕셔너리 생성
        widget_dict = { comp.tag_model.Name: comp for comp in tag_comp_list }
        # 2. 리스트를 순회하며 조건부 활성화가 필요한 위젯들 세팅
        for dependent_comp in tag_comp_list:
            condition = getattr(dependent_comp.tag_model, "EnableCondition", None)
            
            if condition:
                target_name = condition.get("TargetName")
                enable_values = condition.get("EnableValues", [])
                
                target_comp = widget_dict.get(target_name)
                
                if target_comp:
                    # 3. 대상 위젯(TagWidget)의 값이 변할 때 발생하는 시그널 연동
                    # (tag_widget.py 에 정의해두신 user_input_changed 시그널 등을 활용)
                    target_comp.user_input_changed.connect(
                        lambda new_val, comp=dependent_comp, vals=enable_values: comp.setEnabled(new_val in vals)
                    )
                    
                    # 4. 화면을 처음 그릴 때 초기 상태 반영
                    # 위젯에서 현재 UI의 값을 읽어오는 메서드가 필요함
                    current_val = target_comp.get_current_ui_value() 
                    dependent_comp.setEnabled(current_val in enable_values)        
