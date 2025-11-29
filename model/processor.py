import cv2
import numpy as np
import pygame
from model.settings import Settings
from PIL import ImageFont, ImageDraw, Image

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

    def add_emoji(self, idx):
        # 추가할 이모지에 대한 초기화
        emoji = Settings.EMOJIES[idx]
        emoji = cv2.resize(emoji, (200, 200))

        # four_cut은 변경될 네 컷, original은 초기 네 컷
        four_cut = self.four_cut
        original_four_cut = four_cut.copy()
        self.util_processor.main_stack.append(original_four_cut)

        # 이모지를 추가할 opencv 창 설정
        title = 'Add Sticker~'
        cv2.imshow(title, four_cut)

        param = {"title": title, "emoji": emoji, "original_emoji": emoji, "four_cut": four_cut, "original_four_cut": original_four_cut, "center": None}
        cv2.setMouseCallback(title, self.util_processor.onMouse_Emoji, param)
        cv2.createTrackbar('Rotate', title, 0, 360, self.util_processor.onChange)

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

    def onMouse_Emoji(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # 버튼 클릭시 객체의 param에 값 저장
            self.param = param
            param['center'] = (x, y)

            title = param['title']
            four_cut = param['four_cut']
            original_four_cut = param['original_four_cut']
            emoji = param['emoji']

            # 통과 마스크 생성
            masks = cv2.threshold(emoji, 220, 255, cv2.THRESH_BINARY)[1]
            masks = cv2.split(masks)
            foreground_mask = cv2.bitwise_or(masks[0], masks[1])
            foreground_mask = cv2.bitwise_or(foreground_mask, masks[2])
            background_mask = cv2.bitwise_not(foreground_mask)

            # 이모지의 크기를 기준으로 중심으로부터 y, x 시작점 잡기
            h, w = emoji.shape[:2]
            if self.before_roi is not None:
                by, bx = self.before_roi
                four_cut[by:by+h, bx:bx+w] = original_four_cut[by:by+h, bx:bx+w]
            
            return_value = self.calculate_mask(four_cut, emoji, x, y, foreground_mask, background_mask)
            
            self.param['four_cut'] = return_value[0]
            self.before_roi = return_value[1]
            self.param['fg_mask'] = foreground_mask
            self.param['original_fg_mask'] = foreground_mask
            self.param['size_value'] = 1.0

        if event == cv2.EVENT_MOUSEWHEEL:
            if self.param == None:
                return
            
            four_cut = self.param['four_cut']
            original_four_cut = self.param['original_four_cut']
            emoji = self.param['emoji']
            original_emoji = self.param['original_emoji']
            fg_mask = self.param['original_fg_mask']
            x, y = self.param['center']
            MIN_SIZE = 20
            MAX_SIZE = 800
            
            # 이전 영역은 되돌리기(크기가 작아지는 걸 고려하여 크기 변경 전 수행)
            if self.before_roi is not None:
                by, bx = self.before_roi
                h, w = emoji.shape[:2]
                four_cut[by:by+h, bx:bx+w] = original_four_cut[by:by+h, bx:bx+w]

            # 크기 값에 가중치를 더하여 resize 연산
            value = self.param['size_value'] * 1.05 if flags > 0 else self.param['size_value'] * 0.95
            new_h = int(emoji.shape[0] * value)
            new_w = int(emoji.shape[1] * value)

            if new_h < MIN_SIZE or new_h > MAX_SIZE:
                return
            
            new_emoji = cv2.resize(original_emoji, (new_w, new_h))

            h, w = new_emoji.shape[:2]

            # 마스크도 똑같이 resize 연산 수행
            new_fg_mask = cv2.resize(fg_mask, (new_w, new_h))
            new_fg_mask = cv2.threshold(new_fg_mask, 127, 255, cv2.THRESH_BINARY)[1]
            new_bg_mask = cv2.bitwise_not(new_fg_mask)


            return_value = self.calculate_mask(four_cut, new_emoji, x, y, new_fg_mask, new_bg_mask)

            self.param['four_cut'] = return_value[0]
            self.before_roi = return_value[1]
            self.param['emoji'] = new_emoji
            self.param['fg_mask'] = new_fg_mask

    def onChange(self, value):
        if self.param['center'] is None:
            return
        
        four_cut = self.param['four_cut']
        original_four_cut = self.param['original_four_cut']
        emoji = self.param['emoji']
        fg_mask = self.param['fg_mask']
        x, y = self.param['center']

        # 트랙바 크기(각도)만큼 회전 연산
        rotate_emoji = self.rotate(emoji, value)
        h, w = rotate_emoji.shape[:2]

        # 이전 영역은 되돌리기
        if self.before_roi is not None:
            by, bx = self.before_roi
            four_cut[by:by+h, bx:bx+w] = original_four_cut[by:by+h, bx:bx+w]
        
        # 마스크들도 똑같이 회전 연산 수행
        rotate_fg_mask = self.rotate(fg_mask, value)
        rotate_fg_mask = cv2.threshold(rotate_fg_mask, 127, 255, cv2.THRESH_BINARY)[1]
        rotate_bg_mask = cv2.bitwise_not(rotate_fg_mask)

        return_value = self.calculate_mask(four_cut, rotate_emoji, x, y, rotate_fg_mask, rotate_bg_mask)
        
        self.param['four_cut'] = return_value[0]
        self.before_roi = return_value[1]

    def onMouse_Text(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.param = param
            title = self.param['title']
            text = self.param['text']
            four_cut = self.param['four_cut']
            original_four_cut = self.param['original_four_cut']

            if self.before_roi is not None:
                four_cut= original_four_cut # 원본으로 통으로 대체
            
            pil_img = Image.fromarray(cv2.cvtColor(four_cut, cv2.COLOR_BGR2RGB))
            font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 25)
            draw = ImageDraw.Draw(pil_img)

            bbox = draw.textbbox((0, 0), text, font=font, stroke_width=1)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            x = x - text_w // 2
            y = y - text_h // 2

            draw.text((x, y), text, font=font, fill=(255, 255, 255), stroke_width=1)

            four_cut = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            self.param['four_cut'] = four_cut
            self.param['center'] = (y, x)
            self.before_roi = (y, x) # 그냥 아무 값이나 넣기
            cv2.imshow(title, four_cut)

    def calculate_mask(self, four_cut, emoji, x, y, foreground_mask, background_mask):
        title = self.param['title']

        # emoji의 시작점 잡기
        h, w = emoji.shape[:2]
        y = y-h //2
        x = x-w //2

        # 클릭한 위치로부터 이모지가 four_cut 크기를 벗어났을 때를 고려하여 새로 시작점 잡기
        y1 = max(0, y)
        y2 = min(y+h, four_cut.shape[0])
        x1 = max(0, x)
        x2 = min(x+w, four_cut.shape[1])

        # four_cut 내의 관심 영역 잡기(벗어남 고려)
        roi = four_cut[y1:y2, x1:x2]

        # roi를 기준으로 emoji와 mask에도 관심 영역 정하기
        cut_y1 = y1 - y
        cut_y2 = cut_y1 + roi.shape[0]
        cut_x1 = x1 -x
        cut_x2 = cut_x1 + roi.shape[1]

        emoji_cut = emoji[cut_y1:cut_y2, cut_x1:cut_x2]
        fg_mask_cut = foreground_mask[cut_y1:cut_y2, cut_x1:cut_x2]
        bg_mask_cut = background_mask[cut_y1:cut_y2, cut_x1:cut_x2]

        background = cv2.bitwise_and(roi, roi, mask=bg_mask_cut)
        foreground = cv2.bitwise_and(emoji_cut, emoji_cut, mask=fg_mask_cut)

        dst = cv2.add(background, foreground)
        four_cut[y1:y2, x1:x2] = dst

        cv2.imshow(title, four_cut)
        return four_cut, (y1, x1)
        
    def rotate(self, img, value):
        h, w = img.shape[:2]
        center = (w//2, h//2)

        # 중앙 기준 (코, 마사, 사, 코) + index 2위치에 center 기준 보정값
        rot_mat = cv2.getRotationMatrix2D(center, -value, 1)

        # 어파인 변환
        rotate_emoji = cv2.warpAffine(img, rot_mat, (w, h))
        return rotate_emoji

# 이미지 촬영 담당 프로세서
class TakePictureProcessor():
    def __init__(self):
        pygame.mixer.init()

    def take_picture(self, frame):
        shutter = pygame.mixer.Sound("sounds/capture_sound.mp3")
        shutter.play()
        image = cv2.flip(cv2.resize(frame, (Settings.TARGET_WIDTH, Settings.TARGET_HEIGHT)), 1)
        return image