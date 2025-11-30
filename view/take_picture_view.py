from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QDesktopWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from model.settings import Settings
import cv2
import numpy as np

class Communicate(QObject):
    time_out = pyqtSignal()

class TakePictureView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("사진 촬영 (4장)")
        self.setWindowIcon(QIcon(Settings.MAIN_ICON))
        self.setFixedSize(2000, 1500)

        self.current_sec = Settings.CAMERA_TIME
        self.c = Communicate()

        self.top_bar = QHBoxLayout()
        self.second_count = QLabel(self)
        self.second_count.setText(f'{self.current_sec}')
        self.second_count.setFixedSize(200, 200)
        self.second_count.setStyleSheet("background-color: rgb(255, 255, 255); color: black; font-size: 60px; font-weight: bold;")
        self.second_count.setAlignment(Qt.AlignCenter)

        self.capture_count = QLabel(self)
        self.capture_count.setGeometry(800, 30, 400, 150)
        self.capture_count.setStyleSheet("background-color: rgba(0, 0, 0, 100); color: white; font-size: 40px; font-weight: bold; padding: 10px;")
        self.capture_count.setAlignment(Qt.AlignCenter)
        self.capture_count.setText("0 / 4")
        self.capture_count.raise_()
        self.top_bar.addWidget(self.second_count)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.capture_count)
        self.top_bar.addStretch()

        self.cam = QLabel(self)
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

        self.sec_timer = QTimer()
        self.sec_timer.timeout.connect(self.update_count)
        self.sec_timer.start(1000)

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

    def update_count(self):
        self.current_sec -= 1
        self.second_count.setText(f'{self.current_sec}')
        if self.current_sec <= 3:
            self.second_count.setStyleSheet("background-color: rgb(255, 255, 255); color: red; font-size: 60px; font-weight: bold;")
        if self.current_sec == 0:
            self.sec_timer.stop()
            self.c.time_out.emit()
            self.sec_timer.start(1000)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())