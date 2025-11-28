import cv2
import numpy as np
import pygame
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
        count = 0
        for (y1, y2, x1, x2) in self.captured_img_rois:
            self.four_cut[y1:y2, x1:x2] = self.captured_images[count]
            count+=1

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

    def add_emoji(self, idx):
        emoji = Settings.EMOJIES[idx]
        emoji = cv2.resize(emoji, (200, 200))
        four_cut = self.four_cut
        original = four_cut.copy()
        self.util_processor.main_stack.append(original)
        title = 'Add Sticker!'
        cv2.imshow(title, four_cut)
        cv2.createTrackbar('Rotate', title, 0, 360, self.util_processor.onChange)
        param = {"title": title, "emoji": emoji, "four_cut": four_cut, "original": original, "center": None}
        cv2.setMouseCallback(title, self.util_processor.onMouse, param)

        while True:
            key = cv2.waitKeyEx(100)

            if key == 13:
                four_cut = self.util_processor.param["four_cut"]
                self.four_cut = four_cut
                break
        
        cv2.destroyAllWindows()
        return four_cut

class UtilProcessor:
    def __init__(self):
        self.main_stack = []
        self.sub_stack = []
        self.param = None
        self.before_roi = None

    def reset(self):
        self.main_stack.clear()
        self.sub_stack.clear()

    def onMouse(self, event, x, y, flags, param):
        self.param = param
        title = param['title']
        emoji = param['emoji']
        four_cut = param['four_cut']
        original = param['original']
        h, w = emoji.shape[:2]
        background_mask = cv2.threshold(emoji, 220, 255, cv2.THRESH_BINARY)[1]
        foreground_mask = cv2.bitwise_not(background_mask)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.param['center'] = (y, x)
            if self.before_roi is not None:
                by, bx = self.before_roi
                four_cut[by:by+h, bx:bx+w] = original[by:by+h, bx:bx+w]

            y = y-h //2
            x = x-w //2

            y1 = max(0, y)
            y2 = min(y+h, four_cut.shape[0])
            x1 = max(0, x)
            x2 = min(x+w, four_cut.shape[1])

            roi = four_cut[y1:y2, x1:x2]

            mask_x1 = x1 -x
            mask_x2 = mask_x1 + roi.shape[1]
            mask_y1 = y1 - y
            mask_y2 = mask_y1 + roi.shape[0]

            fg_mask_cut = foreground_mask[mask_y1:mask_y2, mask_x1:mask_x2]
            bg_mask_cut = background_mask[mask_y1:mask_y2, mask_x1:mask_x2]
            emoji_cut = emoji[mask_y1:mask_y2, mask_x1:mask_x2]
            emoji_cut = cv2.cvtColor(emoji_cut, cv2.COLOR_GRAY2BGR)

            background = cv2.bitwise_and(roi, roi, mask=bg_mask_cut)
            foreground = cv2.bitwise_and(emoji_cut, emoji_cut, mask=fg_mask_cut)
            dst = cv2.add(background, foreground)
            four_cut[y1:y2, x1:x2] = dst

            self.before_roi = (y1, x1)
            self.param['four_cut'] = four_cut
            self.param['fg_mask'] = fg_mask_cut
            cv2.imshow(title, four_cut)
    
    def onChange(self, value):
        p = self.param
        if p['center'] is None:
            return
        
        title = p['title']
        original = p['original'].copy()
        emoji = p['emoji']
        fg_mask = p['fg_mask']
        y, x = p['center']

        rotate_emoji = self.rotate(emoji, value)
        rotate_fg_mask = self.rotate(fg_mask, value)
        rotate_bg_mask = cv2.bitwise_not(rotate_fg_mask)

        h, w = rotate_emoji.shape[:2]
        y1 = y-h //2
        y2 = y1+h
        x1 = x-w //2
        x2 = x1+w

        H, W = original.shape[:2]

        cut_y1 = max(0, y1)
        cut_y2 = min(H, y2)
        cut_x1 = max(0, x1)
        cut_x2 = min(W, x2)

        e_y1 = cut_y1 - y1
        e_y2 = e_y1 + (cut_y2 - cut_y1)
        e_x1 = cut_x1 - x1
        e_x2 = e_x1 + (cut_x2 - cut_x1)

        emoji_cut = rotate_emoji[e_y1:e_y2, e_x1:e_x2]
        fg_mask_cut = rotate_fg_mask[e_y1:e_y2, e_x1:e_x2]
        bg_mask_cut = rotate_bg_mask[e_y1:e_y2, e_x1:e_x2]

        emoji_cut = cv2.cvtColor(emoji_cut, cv2.COLOR_GRAY2BGR)

        roi = original[cut_y1:cut_y2, cut_x1:cut_x2]
        background = cv2.bitwise_and(roi, roi, mask=bg_mask_cut)
        foreground = cv2.bitwise_and(emoji_cut, emoji_cut, mask=fg_mask_cut)

        dst = cv2.add(background, foreground)
        original[cut_y1:cut_y2, cut_x1:cut_x2] = dst

        self.param['four_cut'] = original
        cv2.imshow(title, original)
        
    def rotate(self, emoji, value):
        h, w = emoji.shape[:2]
        center = (h//2, w//2)

        rot_mat = cv2.getRotationMatrix2D(center, -value, 1)
        rotate_emoji = cv2.warpAffine(emoji, rot_mat, (w, h), cv2.INTER_LINEAR)
        return rotate_emoji

class TakePictureProcessor():
    def __init__(self):
        pygame.mixer.init()

    def take_picture(self, frame):
        shutter = pygame.mixer.Sound("sounds/capture_sound.mp3")
        shutter.play()
        image = cv2.flip(cv2.resize(frame, (Settings.TARGET_WIDTH, Settings.TARGET_HEIGHT)), 1)
        return image