from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from model.settings import Settings
import cv2
import numpy as np

class TakePictureView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("사진 촬영 (4장)")
        self.setWindowIcon(QIcon(Settings.MAIN_ICON))
        self.setFixedSize(2000, 1500)

        self.capture_count = QLabel(self)
        self.capture_count.setGeometry(800, 30, 400, 150)
        self.capture_count.setStyleSheet("""
            background-color: rgba(0, 0, 0, 100);
            color: white;
            font-size: 40px;
            font-weight: bold;
            padding: 10px;
        """)
        self.capture_count.setAlignment(Qt.AlignCenter)
        self.capture_count.setText("0 / 4")
        self.capture_count.raise_()

        self.cam = QLabel(self)
        # self.cam.setGeometry(270, 120, Settings.TARGET_WIDTH*4, Settings.TARGET_HEIGHT*3)
        self.cam.setAlignment(Qt.AlignCenter)

        self.capture_btn = QPushButton("촬영")
        self.capture_btn.setFixedSize(300, 200)
        self.capture_btn.setStyleSheet("font-size: 30px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(200, 200, 200, 100)
        layout.addWidget(self.cam)
        layout.addWidget(self.capture_btn, alignment=Qt.AlignCenter | Qt.AlignBottom)

        self.setLayout(layout)

        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, Settings.TARGET_WIDTH*4)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, Settings.TARGET_HEIGHT*3)
        self.isCapturing = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        if self.isCapturing:
            black = np.zeros((Settings.TARGET_HEIGHT*3, Settings.TARGET_WIDTH*4, 3), np.uint8)
            pix = Settings.convert_to_pyqt_img(black)
            self.cam.setPixmap(pix)
            self.isCapturing = False
            return
        
        ret, frame = self.video.read()
        if not ret:
            return
        
        enhanced_frame = Settings.enhance_frame(frame)
        pix = Settings.convert_to_pyqt_img(cv2.flip(enhanced_frame, 1))
        self.cam.setPixmap(pix)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())