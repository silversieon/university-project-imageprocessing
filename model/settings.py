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

    EMOJIES = [
        cv2.bitwise_not(cv2.imread('images/emoji/emotionless.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/happy.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/sad.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/angry.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/money_happy.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/bad.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/wrath.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/eat.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/up.png', cv2.IMREAD_GRAYSCALE)),
        cv2.bitwise_not(cv2.imread('images/emoji/cry.png', cv2.IMREAD_GRAYSCALE)),
    ]

    # 이미지 변환 함수 (OpenCV -> PyQt)
    def convert_to_pyqt_img(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = image.shape
        image = QImage(image.data, w, h, ch * w, QImage.Format_RGB888)

        pix = QPixmap.fromImage(image)
        return pix
    
    # 프레임 선명도 향상 함수(노이즈 제거 + 선명도 증가)
    def enhance_frame(frame):
        median_frame = cv2.medianBlur(frame, 3) # 미디언 블러로 노이즈 다량 제거
        blur_frame = cv2.GaussianBlur(median_frame, (0, 0), 2) # 가우시안 블러로 부드럽게 처리

        # 선명도 향상(원본 이미지 비율은 높게, 블러 처리 된 부분 가중치도 높여 선명하게)
        sharp_frame = cv2.addWeighted(median_frame, 2.0, blur_frame, -1.0, 0)
        return sharp_frame