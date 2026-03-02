import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont, QFontDatabase
from ui.windows.home.home_window import HomeWindow
from ui.theme.ntheme import NTheme  # 방금 만든 클래스
import resources_rc  

def main():
    # 1. Windows AppUserModelID 설정 (작업 표시줄 그룹화 및 아이콘 분리)
    try:
        myappid = 'company.nvmpro.1.0.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)

    # 1. 테마 초기화 및 적용
    theme = NTheme()
    theme.set_theme("light")
    
    # 2. 앱 전체 아이콘 설정 (작업 표시줄 아이콘 해결의 핵심)
    app.setWindowIcon(QIcon(":/assets/icons/nova_icon.ico"))

    # 3. 리소스 폰트 로드 및 전체 적용
    font_id = QFontDatabase.addApplicationFont(":/assets/fonts/D2Coding.ttf")
    if font_id != -1:  # 폰트 로드 성공 여부 체크
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            # 폰트 패밀리 이름으로 QFont 객체 생성 후 기본 폰트로 지정 (10은 기본 사이즈)
            app.setFont(QFont(font_families[0], 12))
    else:
        print("[경고] D2Coding 폰트를 리소스에서 로드하는데 실패했습니다.")

    window = HomeWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()