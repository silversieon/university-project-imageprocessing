import cv2
import numpy as np
import pygame
from PyQt5.QtGui import QImage, QPixmap
from model.settings import Settings

class MainProcessor():
    def __init__(self):
        self.captured_images = []
        self.captured_count = 0
        self.four_cut = cv2.imread('images/frame/default_frame.png', cv2.IMREAD_COLOR)
        self.captured_img_rois = [[y, y + Settings.TARGET_HEIGHT, 
                                    x, x + Settings.TARGET_WIDTH] for (y, x) in Settings.FOURCUT_POINTS]
        self.foreground_mask = self.set_foreground_mask()
        self.background_mask =  cv2.bitwise_not(self.foreground_mask)

    def set_foreground_mask(self):
        mask = cv2.threshold(cv2.cvtColor(self.four_cut, cv2.COLOR_BGR2GRAY), 50, 255, cv2.THRESH_BINARY)[1]
        return mask
    
    def reset(self):
        self.captured_images = []
        self.captured_count = 0
        self.four_cut = cv2.imread('images/frame/default_frame.png', cv2.IMREAD_COLOR)
    
    def save_images(self, captured_image):
        Settings.enhance_frame(captured_image)
        self.captured_images.append(captured_image)
        y1, y2, x1, x2 = self.captured_img_rois[self.captured_count]
        self.four_cut[y1:y2, x1:x2] = captured_image
        self.captured_count+=1
        return self.captured_count
    
    def save_completed_four_cut(self):
        cv2.imwrite("./four_cut.png", self.four_cut)
        print('save completed fout_cut')

    def convert_to_color(self):
        for idx, (y1, y2, x1, x2) in enumerate(self.captured_img_rois):
            self.four_cut[y1:y2, x1:x2] = self.captured_images[idx]

        return self.four_cut
    
    def convert_to_gray(self):
        for (y1, y2, x1, x2) in self.captured_img_rois:
            roi = self.four_cut[y1:y2, x1:x2]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray_to_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            self.four_cut[y1:y2, x1:x2] = gray_to_bgr

        return self.four_cut
    
    def flip_captured_images(self):
        for (y1, y2, x1, x2) in self.captured_img_rois:
            roi = self.four_cut[y1:y2, x1:x2]
            self.four_cut[y1:y2, x1:x2] = cv2.flip(roi, 1)

        return self.four_cut
    
    def change_background_color(self, idx):
        color = Settings.COLOR_PALETTE[idx]
        rgb = color.lstrip("#")
        r = int(rgb[0:2], 16)
        g = int(rgb[2:4], 16)
        b = int(rgb[4:6], 16)

        bgr = (b, g, r)
        whole = np.full(self.four_cut.shape, bgr, np.uint8)

        colored_background = cv2.bitwise_and(whole, whole, mask=self.background_mask)
        roi   = cv2.bitwise_and(self.four_cut, self.four_cut, mask=self.foreground_mask)

        self.four_cut = cv2.add(colored_background, roi)

        return self.four_cut
    
    def change_background_special(self, idx):
        special_frame = Settings.SPECIAL_FRAMES[idx]
        
        special_background = cv2.bitwise_and(special_frame, special_frame, mask=self.background_mask)
        roi   = cv2.bitwise_and(self.four_cut, self.four_cut, mask=self.foreground_mask)

        self.four_cut = cv2.add(special_background, roi)

        return self.four_cut
    
class TakePictureProcessor():
    def __init__(self):
        pygame.mixer.init()

    def take_picture(self, frame):
        shutter = pygame.mixer.Sound("sounds/capture_sound.mp3")
        shutter.play()
        image = cv2.flip(cv2.resize(frame, (Settings.TARGET_WIDTH, Settings.TARGET_HEIGHT)), 1)
        return image