import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from model.settings import Settings
from model.util_processor import UtilProcessor

class MainProcessor():
    def __init__(self):
        self.captured_images = []
        self.captured_count = 0
        self.four_cut = cv2.imread('images/frame/default_frame.png', cv2.IMREAD_COLOR)
        self.captured_img_rois = [[y, y + Settings.TARGET_HEIGHT, 
                                    x, x + Settings.TARGET_WIDTH] for (y, x) in Settings.FOURCUT_POINTS]
        self.foreground_mask = self.set_foreground_mask()
        self.background_mask =  cv2.bitwise_not(self.foreground_mask)
        self.img_sticker = None
        self.before_nukki_sticker = None
        self.util_processor = UtilProcessor()

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
    
    def undo_four_cut(self):
        if len(self.util_processor.main_stack) == 0:
            return self.four_cut
        
        pop_four_cut = self.util_processor.main_stack.pop()
        self.util_processor.sub_stack.append(self.four_cut)
        self.four_cut = pop_four_cut
        return pop_four_cut
    
    def redo_four_cut(self):
        if len(self.util_processor.sub_stack) == 0:
            return self.four_cut
        
        pop_four_cut = self.util_processor.sub_stack.pop()
        self.util_processor.main_stack.append(self.four_cut)
        self.four_cut = pop_four_cut
        return pop_four_cut
    
    def load_img(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "이미지 선택",
            "./",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            img = cv2.imread(file_path)
            img = cv2.resize(img, (300, 400))
            h, w = img.shape[:2]
            self.img_sticker = img
            self.before_nukki_sticker = cv2.resize(img, (w*3, h*3))
            return img
        
    def add_img(self):
        if self.img_sticker is None:
            return None
        
        img_sticker = self.img_sticker
        img_sticker = cv2.resize(img_sticker, (150, 200))

        # four_cut은 변경될 네 컷, original은 초기 네 컷
        four_cut = self.four_cut
        original_four_cut = four_cut.copy()
        self.util_processor.main_stack.append(original_four_cut)

        # 이미지 스티커를 추가할 opencv 창 설정
        title = 'Add Image Sticker~'
        cv2.imshow(title, four_cut)

        param = {"title": title, "sticker": img_sticker, "original_sticker": img_sticker, "four_cut": four_cut, "original_four_cut": original_four_cut, "center": None}
        cv2.setMouseCallback(title, self.util_processor.onMouse_Sticker, param)

        while True:
            key = cv2.waitKeyEx(100)

            if key == 13:
                four_cut = self.util_processor.param["four_cut"]
                self.four_cut = four_cut
                break
        
        cv2.destroyAllWindows()
        return four_cut
    
    def cut_img(self):
        if self.img_sticker is None:
            return None
        
        original_img_sticker = self.img_sticker
        h, w = original_img_sticker.shape[:2]
        img_sticker = cv2.resize(original_img_sticker, (w*3, h*3))
        blured_img_sticker = cv2.GaussianBlur(img_sticker, (0, 0), 5)
        H, W = img_sticker.shape[:2]
        title = 'cut image sticker!'
        small = np.array((12, 12))
        pts = np.float32([(6, 6), (W-6, 6), (W-6, H-6), (6, H-6)])

        self.util_processor.draw_rect(blured_img_sticker.copy(), img_sticker, pts, small, title)
        param = {"title": title, "small": small, "pts": pts, "img_sticker": img_sticker, 
                "blured_img_sticker": blured_img_sticker}
        cv2.setMouseCallback(title, self.util_processor.onMouse_Cut, param)

        while True:
            key = cv2.waitKeyEx(100)

            if key == 13:
                img_sticker = self.util_processor.save_cropped_img(img_sticker, pts)
                self.img_sticker = img_sticker
                break
        
        cv2.destroyAllWindows()
        return img_sticker
    
    def nukki_img(self):
        if self.img_sticker is None:
            return None
        
        original_img_sticker = self.img_sticker
        h, w = original_img_sticker.shape[:2]
        margin = 1
        rc = (margin, margin, w-margin, h-margin)

        img_sticker = cv2.resize(original_img_sticker, (w*3, h*3))
        H, W = img_sticker.shape[:2]
        self.before_nukki_sticker = img_sticker.copy()

        blured_img_sticker = cv2.GaussianBlur(img_sticker.copy(), (0, 0), 20)

        # 마스크는 검정색으로 채워져있고 입력 영상과 동일한 크기
        mask = np.zeros(original_img_sticker.shape[:2], np.uint8)

        cv2.grabCut(original_img_sticker, mask, rc, None, None, 5, cv2.GC_INIT_WITH_RECT)

        # grabCut 연산에서 mask 0,2는 배경, 1,3은 전경, 따라서 전경만 255로 칠한 마스크 생성
        foreground_mask = np.zeros_like(mask, np.uint8)
        foreground_mask[(mask == 1) | (mask == 3)] = 255
        original_img_sticker = cv2.bitwise_and(original_img_sticker, original_img_sticker, mask=foreground_mask)

        img_sticker = cv2.resize(original_img_sticker, (w*3, h*3))
        cv2.imshow('Nukki In Progress..', blured_img_sticker)

        for x in range(W):
            pt1 = (x, 0)
            pt2 = (x, H)
            blured_img_sticker[0:H, 0:x] = img_sticker[0:H, 0:x]
            cv2.line(blured_img_sticker, pt1, pt2, (0, 255, 0), 3)
            cv2.imshow('Nukki In Progress..', blured_img_sticker)
            cv2.waitKey(5)
        
        cv2.waitKey()
        cv2.destroyAllWindows()

        self.img_sticker = original_img_sticker
        return original_img_sticker
    
    def fine_img(self):
        if self.img_sticker is None:
            return None
        
        title = 'img_sticker'
        sub_title = 'fine_work'
        p_size = 3
        original_img_sticker = self.img_sticker
        h, w = original_img_sticker.shape[:2]

        img_sticker = cv2.resize(original_img_sticker, (w*3, h*3))
        H, W = img_sticker.shape[:2]

        fine_work = np.full((H, W), 255, np.uint8)

        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.moveWindow(title, 200, 100)

        cv2.namedWindow(sub_title, cv2.WINDOW_NORMAL)
        cv2.moveWindow(sub_title, 1200, 100)

        cv2.imshow(title, img_sticker)
        cv2.imshow(sub_title, fine_work)
        self.util_processor.fine_stack.append(img_sticker.copy())
        param = {"title": title, "sub_title": sub_title, "img_sticker": img_sticker, "original_img_sticker": original_img_sticker,
                "before_nukki_sticker": self.before_nukki_sticker, "p_size": p_size}
        cv2.setMouseCallback(title, self.util_processor.onMouse_Fine, param)

        while True:
            key = cv2.waitKeyEx(100)

            if key == 13:
                img_sticker = param['original_img_sticker']
                self.img_sticker = img_sticker
                break
            elif key == 8:
                if len(self.util_processor.fine_stack) <= 1:
                    continue

                self.util_processor.fine_stack.pop()
                img_sticker = self.util_processor.fine_stack[-1].copy()

                param['img_sticker'] = img_sticker
                param['original_img_sticker'] = cv2.resize(img_sticker, (w, h))
                
                if 'pos' in self.util_processor.param:
                    x, y = self.util_processor.param['pos']
                    y1 = max(0, y-50)
                    y2 = min(H, y+50)
                    x1 = max(0, x-50)
                    x2 = min(W, x+50)
                    fine_work = img_sticker[y1:y2, x1:x2]
                    fine_work = cv2.resize(fine_work, (W, H))

                cv2.imshow(title, img_sticker)
                cv2.imshow(sub_title, fine_work)
        
        cv2.destroyAllWindows()
        return img_sticker

    def add_emoji(self, idx):
        # 추가할 이모지에 대한 초기화
        emoji = Settings.EMOJIES[idx]
        emoji = cv2.resize(emoji, (200, 200))

        # four_cut은 변경될 네 컷, original은 초기 네 컷
        four_cut = self.four_cut
        original_four_cut = four_cut.copy()
        self.util_processor.main_stack.append(original_four_cut)

        # 이모지를 추가할 opencv 창 설정
        title = 'Add Emoji Sticker~'
        cv2.imshow(title, four_cut)

        param = {"title": title, "sticker": emoji, "original_sticker": emoji, "four_cut": four_cut, "original_four_cut": original_four_cut, "center": None}
        cv2.setMouseCallback(title, self.util_processor.onMouse_Sticker, param)
        cv2.createTrackbar('Rotate', title, 0, 360, self.util_processor.onChange_Sticker)

        while True:
            key = cv2.waitKeyEx(100)

            if key == 13:
                four_cut = self.util_processor.param["four_cut"]
                self.four_cut = four_cut
                break
        
        cv2.destroyAllWindows()
        return four_cut
    
    def add_text(self, text):
        four_cut = self.four_cut
        original_four_cut = four_cut.copy()
        self.util_processor.main_stack.append(original_four_cut)

        title = 'Add Text~'
        cv2.imshow(title, four_cut)

        param = {"title": title, "text": text, "four_cut": four_cut, "original_four_cut": original_four_cut, "center": None}
        cv2.setMouseCallback(title, self.util_processor.onMouse_Text, param)

        while True:
            key = cv2.waitKeyEx(100)

            if key == 13:
                four_cut = self.util_processor.param["four_cut"]
                self.four_cut = four_cut
                break
        
        cv2.destroyAllWindows()
        return four_cut