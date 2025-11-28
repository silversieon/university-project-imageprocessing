from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDesktopWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from model.settings import Settings

class EmojiStickerSettingView(QWidget):
    def __init__(self, main_processor):
        super().__init__()
        self.setWindowTitle('귀여운 이모지 세팅 및 문구 추가')
        self.setWindowIcon(QIcon(Settings.MAIN_ICON))
        self.setFixedSize(2000, 1500)

        self.top_bar = QHBoxLayout()
        self.save_btn = QPushButton("⭐이미지 저장⭐")
        self.set_top_bar()

        self.left_bar = QVBoxLayout()
        self.emoji_btn = []
        self.undo_btn = QPushButton("실행\n취소")
        self.redo_btn = QPushButton("다시\n실행")
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
        self.save_btn.setFixedSize(200, 100)

        center_layout = QHBoxLayout()

        self.top_bar.addWidget(self.save_btn)
        self.top_bar.addLayout(center_layout)
        self.top_bar.addStretch()
        
    def set_left_bar(self):

        self.left_bar.setContentsMargins(20, 20, 20, 20)
        emojies = Settings.EMOJIES

        for i in range(0, len(emojies), 2):
            row = QHBoxLayout()

            btn1 = QPushButton()
            btn1.setFixedSize(80, 80)
            btn1.setProperty("emoji", i)
            pix1 = Settings.convert_to_pyqt_img(emojies[i])
            btn1.setIcon(QIcon(pix1))
            btn1.setIconSize(btn1.size())
            btn1.setStyleSheet("border-radius: 25px; border: 1px solid #ccc;")
            self.emoji_btn.append(btn1)
            row.addWidget(btn1)

            if i + 1 < len(emojies):
                btn2 = QPushButton()
                btn2.setFixedSize(80, 80)
                btn2.setProperty("emoji", i+1)
                pix2 = Settings.convert_to_pyqt_img(emojies[i+1])
                btn2.setIcon(QIcon(pix2))
                btn2.setIconSize(btn2.size())
                btn2.setStyleSheet("border-radius: 25px; border: 1px solid #ccc;")
                self.emoji_btn.append(btn2)
                row.addWidget(btn2)

            self.left_bar.addLayout(row)
        
        self.left_bar.addStretch()

        # undo, redo에 대한 row
        row = QHBoxLayout()
        self.undo_btn.setFixedSize(80, 150)
        self.undo_btn.setStyleSheet("background-color: #000000; color: white; font-weight: bold;")
        self.redo_btn.setFixedSize(80, 150)
        self.redo_btn.setStyleSheet("background-color: #000000; color: white; font-weight: bold;")

        row.addWidget(self.undo_btn)
        row.addWidget( self.redo_btn)
        self.left_bar.addLayout(row)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())