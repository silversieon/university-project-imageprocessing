from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QDesktopWidget, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from model.settings import Settings
import cv2

class BasicSettingView(QWidget):
    def __init__(self, main_processor):
        super().__init__()
        self.setWindowTitle("네 컷 기본 설정")
        self.resize(2000, 1500)
        self.setWindowIcon(QIcon(Settings.MAIN_ICON))

        self.top_bar = QHBoxLayout()
        self.next_btn = QPushButton("다음으로")
        self.color_btn = QPushButton()
        self.gray_btn = QPushButton()
        self.flip_btn = QPushButton("↔")
        self.set_top_bar()

        self.left_bar = QVBoxLayout()
        self.color_palette_btn = []
        self.special_frame_btn = []
        self.retry_btn = QPushButton("다시 촬영")
        self.set_left_bar()

        self.main_area = QLabel()
        self.main_area.setStyleSheet("background-color: #d9d9d9; border: 1px solid black;")
        self.main_area.setAlignment(Qt.AlignCenter)
        pix = Settings.convert_to_pyqt_img(main_processor.four_cut)
        self.main_area.setPixmap(pix)

        self.layout = QVBoxLayout()

        # 상단 바 위젯 추가
        self.top_widget = QWidget()
        self.top_widget.setLayout(self.top_bar)
        self.top_widget.setStyleSheet("background-color: #d9d9d9; border: 1px solid black;")
        self.layout.addWidget(self.top_widget)

        # (좌측 바 + 메인 영역) 위젯 추가
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_bar)
        self.left_widget.setStyleSheet("background-color: #d9d9d9; border: 1px solid black;")

        self.middle = QHBoxLayout()
        self.middle.addWidget(self.left_widget)
        self.middle.addWidget(self.main_area, stretch=1)

        self.middle_widget = QWidget()
        self.middle_widget.setLayout(self.middle)
        self.layout.addWidget(self.middle_widget, stretch=1)

        self.setLayout(self.layout)

    def update_main_area(self, four_cut):
        pix = Settings.convert_to_pyqt_img(four_cut)
        self.main_area.setPixmap(pix)

    def set_top_bar(self):
        self.next_btn.setFixedSize(200, 100)

        self.color_btn.setFixedSize(40, 40)
        self.color_btn.setStyleSheet("background-color: white; border-radius: 20px;")

        self.gray_btn.setFixedSize(40, 40)
        self.gray_btn.setStyleSheet("background-color: black; border-radius: 20px;")

        self.flip_btn.setFixedSize(40, 40)
        self.flip_btn.setStyleSheet("background-color: black; color: white; border-radius: 20px;")

        center_layout = QHBoxLayout()
        center_layout.addWidget(self.color_btn)
        center_layout.addWidget(self.gray_btn)
        center_layout.addWidget(self.flip_btn)
        center_layout.setSpacing(20)

        self.top_bar.addWidget(self.next_btn)
        self.top_bar.addStretch()
        self.top_bar.addLayout(center_layout)
        self.top_bar.addStretch()
        
    def set_left_bar(self):

        self.left_bar.setContentsMargins(20, 20, 20, 20)
        colors = Settings.COLOR_PALETTE
        special_frame_icons = Settings.SPECIAL_FRAME_ICONS

        for i in range(0, len(colors), 2):
            row = QHBoxLayout()

            btn1 = QPushButton()
            btn1.setFixedSize(50, 50)
            btn1.setProperty("color", colors[i])
            btn1.setStyleSheet(f"background-color: {colors[i]}; border-radius: 25px; border: 1px solid #ccc;")
            self.color_palette_btn.append(btn1)
            row.addWidget(btn1)

            if i + 1 < len(colors):
                btn2 = QPushButton()
                btn2.setFixedSize(50, 50)
                btn2.setProperty("color", colors[i+1])
                btn2.setStyleSheet(f"background-color: {colors[i+1]}; border-radius: 25px; border: 1px solid #ccc;")
                self.color_palette_btn.append(btn2)
                row.addWidget(btn2)

            self.left_bar.addLayout(row)

        self.left_bar.addStretch()

        for i in range(0, len(special_frame_icons), 2):
            row = QHBoxLayout()

            btn1 = QPushButton()
            btn1.setFixedSize(80, 60)
            btn1.setProperty("special_idx", i)
            pix1 = Settings.convert_to_pyqt_img(special_frame_icons[i])
            btn1.setIcon(QIcon(pix1))
            btn1.setIconSize(btn1.size())
            self.special_frame_btn.append(btn1)
            row.addWidget(btn1)

            if i + 1 < len(special_frame_icons):
                btn2 = QPushButton()
                btn2.setFixedSize(80, 60)
                btn2.setProperty("special_idx", i+1)
                pix2 = Settings.convert_to_pyqt_img(special_frame_icons[i+1])
                btn2.setIcon(QIcon(pix2))
                btn2.setIconSize(btn2.size())
                self.special_frame_btn.append(btn2)
                row.addWidget(btn2)

            self.left_bar.addLayout(row)
        
        self.left_bar.addStretch()
        row = QHBoxLayout()
        self.retry_btn.setFixedSize(150, 100)
        self.retry_btn.setStyleSheet("background-color: #000000; color: white; font-weight: bold;")
        row.addWidget(self.retry_btn)
        self.left_bar.addLayout(row)
        self.left_bar.addStretch()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())