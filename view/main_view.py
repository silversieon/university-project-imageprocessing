from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
import numpy as np


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing - MVC")

        self.open_btn = QPushButton("Open Image")
        self.gray_btn = QPushButton("Gray Convert")
        self.image_label = QLabel("No image loaded")

        layout = QVBoxLayout()
        layout.addWidget(self.open_btn)
        layout.addWidget(self.gray_btn)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def display_image(self, img):
        """ img is numpy array """
        # handle None gracefully (e.g. failed load)
        if img is None:
            self.image_label.setText("Failed to load image")
            return
        h, w = img.shape[:2]
        if img.ndim == 2:  # gray
            qimg = QImage(img, w, h, w, QImage.Format_Grayscale8)
        else:
            qimg = QImage(img.data, w, h, 3 * w, QImage.Format_BGR888)

        self.image_label.setPixmap(QPixmap.fromImage(qimg))