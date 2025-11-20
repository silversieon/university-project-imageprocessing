from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from model.settings import Settings
import cv2

class TakePictureView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("사진 촬영 (4장)")
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setFixedSize(900, 900)

        self.cam = QLabel(self)
        self.cam.setGeometry(270, 120, Settings.TARGET_WIDTH, Settings.TARGET_HEIGHT)
        self.cam.setAlignment(Qt.AlignCenter)

        self.capture_btn = QPushButton("촬영")

        layout = QVBoxLayout()
        layout.setContentsMargins(200, 100, 200, 100)
        layout.addWidget(self.cam)
        layout.addWidget(self.capture_btn)

        self.setLayout(layout)

        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, Settings.TARGET_WIDTH)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, Settings.TARGET_HEIGHT)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return

        pix = Settings.convert_to_pyqt_img(cv2.flip(frame, 1))
        self.cam.setPixmap(pix)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())