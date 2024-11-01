#
#
# EasyWIFI - easy way to change wifi
# ONLY FOR **KOREAN**
# ver 1.0.0
#
# Copyright (C) 2024 Yeongjun Hwang
#
# This program is licensed under the MIT License.
# See the LICENSE file for details.
#
# 
# It’s advisable to read the Qt license specifics on the official website:
# https://doc.qt.io/qtforpython/licenses.html
# ///////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////



import sys, os
import ezwifi

from tendo import singleton
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QAction




class EasyWIFI(QWidget):
    def __init__(self):
        super().__init__()

        # UI 구성
        self.setWindowTitle("EasyWIFI")
        self.setGeometry(0, 0, 300, 100)  # 초기 크기 설정
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)  # 상단 바 없애기
        icon = QIcon.fromTheme("applications-internet")
        self.setWindowIcon(icon)

        layout = QVBoxLayout()

        self.network_list = QListWidget()
        self.set_list_widget_style()
        self.load_networks()
        layout.addWidget(self.network_list)

        self.connect_button = QPushButton("연결")
        self.connect_button.clicked.connect(self.connect_to_network)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)
        self.adjust_window_size()
        self.move_to_bottom_right()

        self.w = ezwifi.Wifi()

        # 시스템 트레이 아이콘 설정
        self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("applications-internet"), self)  # 아이콘 파일 경로
        self.tray_icon.setToolTip("EasyWIFI")  # 툴팁 설정
        self.tray_icon.setVisible(True)
        
        # 트레이 아이콘 메뉴 생성
        menu = QMenu()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)

        menu.addAction(exit_action)
        menu.addAction(hide_action)
        self.tray_icon.setContextMenu(menu)

        self.tray_icon.activated.connect(self.tray_icon_activated)

    def set_list_widget_style(self):
        font = QFont("Segoe UI", 13)
        self.network_list.setFont(font)
    
    def load_networks(self):
        try:
            with open(NETWORK_PATH, "r") as file:
                networks = file.readlines()
                self.network_list.addItems([network.strip() for network in networks])

        except FileNotFoundError:
            QMessageBox.warning(self, "파일 오류", f"networks.txt 파일을 찾을 수 없습니다.")

    def connect_to_network(self):
        selected_network = self.network_list.currentItem()
        if selected_network:
            network_name = selected_network.text()
            with patch('builtins.print') as mock_print:
                self.w.connect(network_name)

            result = None
            try:
                mock_print.assert_any_call(f"{network_name} is connected")
            except AssertionError:
                result = f"{network_name}에 연결할 수 없습니다."
            if not result:
                result = f"{network_name}에 연결되었습니다."

            QMessageBox.information(self, "연결 결과", result)
        else:
            QMessageBox.warning(self, "선택 오류", "연결할 네트워크를 선택하세요.")

    def adjust_window_size(self):
        item_count = self.network_list.count()
        item_height = 30  # 각 요소의 높이 설정
        total_height = item_count * item_height + 50  # 버튼과 여백 고려
        self.resize(300, total_height)

    def move_to_bottom_right(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.width() - self.width()
        y = screen_geometry.height() - self.height() - 40  # 작업 표시줄 높이 고려
        self.move(x, y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.connect_to_network()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()  # 클릭 시 창을 표시
            self.raise_()  # 창을 최상위로 올리기
            self.activateWindow()  # 창을 활성화

    def exit_app(self):
        QApplication.quit()


def preprocess():
    global NETWORK_PATH

    if not sys.executable.endswith("python.exe"): # only on exeutive file
        NETWORK_PATH = os.path.dirname(sys.executable) + r"\networks.txt" # because of pyinstaller onefile option
    else:
        NETWORK_PATH = "networks.txt"

    try:
        m = singleton.SingleInstance() # 중복 실행 방지
    except Exception as e:
        exit()



if __name__ == "__main__":
    NETWORK_PATH = None
    preprocess()

    app = QApplication(sys.argv)
    window = EasyWIFI()
    window.hide()  # 초기화 시 창 숨김
    sys.exit(app.exec())