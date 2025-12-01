from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDesktopWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from model.settings import Settings

class ImgStickerSettingView(QWidget):
    def __init__(self, main_processor):
        super().__init__()
        self.setWindowTitle('추가 이미지 세팅')
        self.setWindowIcon(QIcon(Settings.MAIN_ICON))
        self.setFixedSize(2000, 1500)

        self.top_bar = QHBoxLayout()
        self.next_btn = QPushButton("다음으로➡️")
        self.crop_btn = QPushButton("영역 자르기✂️")
        self.nukki_btn = QPushButton("누끼 따기🖼️")
        self.fine_btn = QPushButton("미세 작업✏️")
        self.set_top_bar()

        self.left_bar = QVBoxLayout()
        self.img_sticker_btn = QPushButton()
        self.img_load_btn = QPushButton("이미지\n불러오기")
        self.undo_btn = QPushButton("실행\n취소")
        self.redo_btn = QPushButton("다시\n실행")
        self.set_left_bar()

        self.main_area = QLabel()
        pix = Settings.convert_to_pyqt_img(main_processor.four_cut)
        self.set_middle(pix)

        self.layout = QVBoxLayout()

        # 상단 바 위젯 추가
        self.top_widget = QWidget()
        self.top_widget.setLayout(self.top_bar)
        self.top_widget.setStyleSheet("background-color: #d9d9d9; border: 1px solid black;")
        self.layout.addWidget(self.top_widget)

        # (좌측 바 + 메인 영역) 위젯 추가
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_bar)
        self.left_widget.setFixedWidth(400)
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
        center_layout = QHBoxLayout()

        self.crop_btn.setFixedSize(180, 80)
        self.crop_btn.setStyleSheet("background-color: #FFFFFF; color: black; font-weight: bold;")
        self.nukki_btn.setFixedSize(180, 80)
        self.nukki_btn.setStyleSheet("background-color: #FFFFFF; color: black; font-weight: bold;")
        self.fine_btn.setFixedSize(180, 80)
        self.fine_btn.setStyleSheet("background-color: #FFFFFF; color: black; font-weight: bold;")

        self.top_bar.addWidget(self.next_btn)
        self.top_bar.addStretch()
        center_layout.addWidget(self.crop_btn)
        center_layout.addSpacing(50)
        center_layout.addWidget(self.nukki_btn)
        center_layout.addSpacing(50)
        center_layout.addWidget(self.fine_btn)
        self.top_bar.addLayout(center_layout)
        self.top_bar.addStretch()
        
    def set_left_bar(self):
        self.left_bar.setContentsMargins(20, 20, 20, 20)
        self.left_bar.addStretch()

        # img_sticker에 대한 row
        row = QHBoxLayout()
        self.img_sticker_btn.setFixedSize(300, 400)
        self.img_sticker_btn.setStyleSheet("background-color: #FFFFFF;")
        row.addWidget(self.img_sticker_btn)
        self.left_bar.addLayout(row)

        # img_load에 대한 row
        row = QHBoxLayout()
        self.img_load_btn.setFixedSize(160, 100)
        self.img_load_btn.setStyleSheet("background-color: #FFFFFF; color: black; font-weight: bold;")
        row.addWidget(self.img_load_btn)
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

    def set_middle(self, pix):
        self.main_area.setStyleSheet("background-color: #d9d9d9; border: 1px solid black;")
        self.main_area.setAlignment(Qt.AlignCenter)
        self.main_area.setPixmap(pix)

    def set_img_sticker_btn(self, loaded_img):
        pix = Settings.convert_to_pyqt_img(loaded_img)
        self.img_sticker_btn.setIcon(QIcon(pix))
        self.img_sticker_btn.setIconSize(pix.size())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())