import cv2
import pygame
from model.settings import Settings

# 이미지 촬영 담당 프로세서
class TakePictureProcessor():
    def __init__(self):
        pygame.mixer.init()

    def take_picture(self, frame):
        shutter = pygame.mixer.Sound("sounds/capture_sound.mp3")
        shutter.play()
        image = cv2.flip(cv2.resize(frame, (Settings.TARGET_WIDTH, Settings.TARGET_HEIGHT)), 1)
        return image