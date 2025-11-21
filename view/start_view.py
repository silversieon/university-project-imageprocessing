from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QToolTip, QDesktopWidget, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication
from model.settings import Settings

class StartView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나만의 네컷 촬영")
        self.setFixedSize(650, 650)
        self.setWindowIcon(QIcon(Settings.MAIN_ICON))

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('나만의 <strong>추억</strong>을 담을 수 있는 네 컷 만들기!')

        self.start_btn = QPushButton("나만의 네 컷 만들기")
        self.start_btn.setToolTip('<b>사진 촬영 시작</b>')
        self.start_btn.setFixedSize(250, 100)

        self.quit_btn = QPushButton("종료", self)
        self.quit_btn.setToolTip('프로그램을 종료합니다')

        layout = QVBoxLayout()
        layout.setContentsMargins(200, 200, 200, 200)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.quit_btn)

        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())