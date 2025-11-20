import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class Settings():
    TARGET_WIDTH = 360
    TARGET_HEIGHT = 480
    FOURCUT_POINTS = [
        [40, 30],
        [40, 410],
        [540, 30],
        [540, 410]
    ]

    COLOR_PALETTE = [
            "#FFFFFF", "#000000", "#F2C3C3", "#E8C19E",
            "#F7F3B8", "#CFF5B6", "#B8F7E3", "#AFCDFB",
            "#9BB8FF", "#B99BFF"
        ]

    def convert_to_pyqt_img(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = image.shape
        image = QImage(image.data, w, h, ch * w, QImage.Format_RGB888)

        pix = QPixmap.fromImage(image)
        return pix