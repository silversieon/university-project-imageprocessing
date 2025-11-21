import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class Settings():
    MAIN_ICON = 'images/icon/main_icon.png'
    WIDTH = 1200
    HEIGHT = 900
    TARGET_WIDTH = 480
    TARGET_HEIGHT = 360
    TARGET_SPACING = 35
    FOURCUT_POINTS = [
        [TARGET_SPACING, TARGET_SPACING],
        [TARGET_SPACING, TARGET_WIDTH + TARGET_SPACING * 2],
        [TARGET_HEIGHT + TARGET_SPACING * 2, TARGET_SPACING],
        [TARGET_HEIGHT + TARGET_SPACING * 2, TARGET_WIDTH + TARGET_SPACING * 2]
    ]

    COLOR_PALETTE = [
            "#FFFFFF", "#000000", "#AA7E63", "#DFC054",
            "#DC6C56", "#80977D", "#C9B68C", "#AEC25F",
            "#55698E", "#CC8AB0"
        ]
    
    SPECIAL_FRAMES = [
        cv2.imread('images/frame/special_frame1.jpg', cv2.IMREAD_COLOR),
        cv2.imread('images/frame/special_frame2.jpg', cv2.IMREAD_COLOR),
        cv2.imread('images/frame/special_frame3.jpg', cv2.IMREAD_COLOR),
        cv2.imread('images/frame/special_frame4.jpg', cv2.IMREAD_COLOR),
        cv2.imread('images/frame/special_frame5.jpg', cv2.IMREAD_COLOR),
        cv2.imread('images/frame/special_frame6.jpg', cv2.IMREAD_COLOR)
    ]

    SPECIAL_FRAME_ICONS = [
        cv2.imread('images/icon/special_icon1.png', cv2.IMREAD_COLOR),
        cv2.imread('images/icon/special_icon2.png', cv2.IMREAD_COLOR),
        cv2.imread('images/icon/special_icon3.png', cv2.IMREAD_COLOR),
        cv2.imread('images/icon/special_icon4.png', cv2.IMREAD_COLOR),
        cv2.imread('images/icon/special_icon5.png', cv2.IMREAD_COLOR),
        cv2.imread('images/icon/special_icon6.png', cv2.IMREAD_COLOR)
    ]

    def convert_to_pyqt_img(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = image.shape
        image = QImage(image.data, w, h, ch * w, QImage.Format_RGB888)

        pix = QPixmap.fromImage(image)
        return pix