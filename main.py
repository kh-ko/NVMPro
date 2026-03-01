import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont
from ui.windows.home.home_window import HomeWindow
from qfluentwidgets import setTheme, Theme, setThemeColor

def main():
    # 1. Windows AppUserModelID 설정 (작업 표시줄 그룹화 및 아이콘 분리)
    try:
        myappid = 'company.nvmpro.1.0.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    
    # [버그 수정] PySide 기본 폰트와 함께 qFluentWidgets의 내부 참조용 폰트를 동시에 강제 설정
    font_family = "Consolas"
    app.setFont(QFont(font_family, 20))
    from qfluentwidgets import qconfig
    qconfig.set(qconfig.fontFamilies, [font_family])
    
    setTheme(Theme.LIGHT)
    setThemeColor('#0078d4')
    # 3. 앱 전체 아이콘 설정 (작업 표시줄 아이콘 해결의 핵심)
    app.setWindowIcon(QIcon("data/assets/image/nova_icon.ico"))

    window = HomeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()