import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

class UtilProcessor:
    def __init__(self):
        # 전체 네 컷을 위한 undo, redo용 스택
        self.main_stack = []
        self.sub_stack = []
        self.param = None
        self.before_roi = None

        # 이미지 크롭(컷)을 위한 check 변수 초기화
        self.check = -1

        # 이미지 미세 작업(fine)을 위한 스택
        self.fine_stack = []

    def reset(self):
        self.main_stack.clear()
        self.sub_stack.clear()
        self.param = None
        self.before_roi = None

    ###################################
    # 이모지 관련 처리 함수들(이미지 스티커, 이모지 모두 포함)
    ###################################
    def onMouse_Sticker(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # 버튼 클릭시 객체의 param에 값 저장
            self.param = param
            param['center'] = (x, y)

            title = param['title']
            four_cut = param['four_cut']
            original_four_cut = param['original_four_cut']
            emoji = param['sticker']

            # 통과 마스크 생성
            masks = cv2.threshold(emoji, 1, 255, cv2.THRESH_BINARY)[1]
            masks = cv2.split(masks)
            foreground_mask = cv2.bitwise_or(masks[0], masks[1])
            foreground_mask = cv2.bitwise_or(foreground_mask, masks[2])
            background_mask = cv2.bitwise_not(foreground_mask)

            # 이모지의 크기를 기준으로 중심으로부터 y, x 시작점 잡기
            h, w = emoji.shape[:2]
            if self.before_roi is not None:
                by, bx = self.before_roi
                four_cut[by:by+h, bx:bx+w] = original_four_cut[by:by+h, bx:bx+w]
            
            return_value = self.add_sticker(four_cut, emoji, x, y, foreground_mask, background_mask)
            self.param['four_cut'] = return_value[0]
            self.before_roi = return_value[1]
            self.param['fg_mask'] = foreground_mask
            self.param['original_fg_mask'] = foreground_mask
            cv2.imshow(title, self.param['four_cut'])

        # if event == cv2.EVENT_RBUTTONDOWN:
        #     if self.param == None:
        #         return

        #     title = self.param['title']
        #     four_cut = self.param['four_cut']
        #     original_four_cut = self.param['original_four_cut']
        #     emoji = self.param['sticker']
        #     original_emoji = self.param['original_sticker']
        #     fg_mask = self.param['fg_mask']
        #     x, y = self.param['center']

        #     # 이전 영역은 되돌리기(크기가 작아지는 걸 고려하여 크기 변경 전 수행)
        #     if self.before_roi is not None:
        #         by, bx = self.before_roi
        #         h, w = emoji.shape[:2]
        #         four_cut[by:by+h, bx:bx+w] = original_four_cut[by:by+h, bx:bx+w]

        #     flipped_emoji = cv2.flip(emoji, 1)
        #     flipped_fg_mask = cv2.flip(fg_mask, 1)
        #     flipped_bg_mask = cv2.bitwise_not(flipped_fg_mask)

        #     return_value = self.add_sticker(four_cut, flipped_emoji, x, y, flipped_fg_mask, flipped_bg_mask)

        #     self.param['four_cut'] = return_value[0]
        #     self.before_roi = return_value[1]
        #     self.param['sticker'] = flipped_emoji
        #     self.param['original_sticker'] = flipped_emoji
        #     self.param['fg_mask'] = flipped_fg_mask
        #     self.param['original_fg_mask'] = flipped_fg_mask
        #     cv2.imshow(title, self.param['four_cut'])

        if event == cv2.EVENT_MOUSEWHEEL:
            if self.param == None:
                return
            
            title = self.param['title']
            four_cut = self.param['four_cut']
            original_four_cut = self.param['original_four_cut']
            emoji = self.param['sticker']
            original_emoji = self.param['original_sticker']
            fg_mask = self.param['original_fg_mask']
            x, y = self.param['center']
            MIN_SIZE_RATE = 0.2
            MAX_SIZE_RATE = 4.0
            
            # 이전 영역은 되돌리기(크기가 작아지는 걸 고려하여 크기 변경 전 수행)
            if self.before_roi is not None:
                by, bx = self.before_roi
                h, w = emoji.shape[:2]
                four_cut[by:by+h, bx:bx+w] = original_four_cut[by:by+h, bx:bx+w]

            # 크기 값에 가중치를 더하여 resize 연산
            if 'size_value' not in self.param:
                self.param['size_value'] = 1.0
            
            size_value = self.param['size_value']
            size_value = size_value * 1.05 if flags > 0 else size_value * 0.95
            
            size_value = max(MIN_SIZE_RATE, min(MAX_SIZE_RATE, size_value))
            self.param['size_value'] = size_value

            new_h = int(original_emoji.shape[0] * size_value)
            new_w = int(original_emoji.shape[1] * size_value)

            new_emoji = cv2.resize(original_emoji, (new_w, new_h))

            h, w = new_emoji.shape[:2]

            # 마스크도 똑같이 resize 연산 수행
            new_fg_mask = cv2.resize(fg_mask, (new_w, new_h))
            new_fg_mask = cv2.threshold(new_fg_mask, 127, 255, cv2.THRESH_BINARY)[1]
            new_bg_mask = cv2.bitwise_not(new_fg_mask)

            return_value = self.add_sticker(four_cut, new_emoji, x, y, new_fg_mask, new_bg_mask)

            self.param['four_cut'] = return_value[0]
            self.before_roi = return_value[1]
            self.param['sticker'] = new_emoji
            self.param['fg_mask'] = new_fg_mask
            cv2.imshow(title, self.param['four_cut'])

    def onChange_Sticker(self, value):
        if self.param['center'] is None:
            return
        
        title = self.param['title']
        four_cut = self.param['four_cut']
        original_four_cut = self.param['original_four_cut']
        emoji = self.param['sticker']
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

        return_value = self.add_sticker(four_cut, rotate_emoji, x, y, rotate_fg_mask, rotate_bg_mask)
        
        self.param['four_cut'] = return_value[0]
        self.before_roi = return_value[1]
        cv2.imshow(title, self.param['four_cut'])

    ###################################
    # 텍스트 관련 처리 함수
    ###################################
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

    ###################################
    # 스티커를 붙이는 함수
    ###################################
    def add_sticker(self, four_cut, emoji, x, y, foreground_mask, background_mask):
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

        return four_cut, (y1, x1)
    
    ###################################
    # 어파인 변환(회전) 함수
    ###################################
    def rotate(self, img, value):
        h, w = img.shape[:2]
        center = (w//2, h//2)

        # 반환값: 중앙 기준 (코, 마사, 사, 코) + index 2위치에 center 기준 보정값
        rot_mat = cv2.getRotationMatrix2D(center, -value, 1)

        # 어파인 변환
        rotate_emoji = cv2.warpAffine(img, rot_mat, (w, h))
        return rotate_emoji
    
    ################################
    # 이미지 크롭 관련 처리 함수들
    ##############################
    def contain_pts(self, p, p1, p2):
        return p1[0] <= p[0] < p2[0] and p1[1] <= p[1] < p2[1]

    def save_cropped_img(self, img, pts):
        pts = pts.astype(int)

        x1, y1 = pts[0]
        x2, y2 = pts[2]
        roi = img[y1:y2, x1:x2]
        roi = cv2.resize(roi, (300, 400))
        return roi

    def draw_rect(self, blured_img, img, pts, small, title):
        pts = pts.astype(int)
        x1, y1 = pts[0]
        x2, y2 = pts[2]
        blured_img[y1:y2, x1:x2] = img[y1:y2, x1:x2]
        
        rois = [(p-small, small * 2) for p in pts]
        for (x,y), (w,h) in np.int32(rois):
            cv2.rectangle(blured_img, (x, y, w, h), (0, 255, 0), 3)
        
        cv2.polylines(blured_img, [pts.astype(int)], True, (0, 255, 0), 3)
        cv2.imshow(title, blured_img)

    def onMouse_Cut(self, event, x, y, flags, param):
        self.param = param
        title = param['title']
        small = param['small']
        pts = param['pts']
        img_sticker = param['img_sticker']
        blured_img_sticker = param['blured_img_sticker']
        if event == cv2.EVENT_LBUTTONDOWN:
            if x > pts[0][0] + 6 and x < pts[1][0] - 6 and y > pts[0][1] + 6 and y < pts[3][1] - 6:
                self.check = -2
                self.pre_pt = (x, y)
                return 
            
            for i, p in enumerate(pts):
                p1, p2 = p - small, p + small
                if self.contain_pts((x,y), p1, p2): 
                    self.check = i
                    self.pre_pt = pts[i].copy()

        if event == cv2.EVENT_LBUTTONUP:
            self.check = -1

        if self.check == -2:
            dx = x - self.pre_pt[0]
            dy = y - self.pre_pt[1]

            pts[:] = pts + (dx, dy)
            self.pre_pt = (x, y)
            self.draw_rect(blured_img_sticker.copy(), img_sticker, pts, small, title)
            return
        
        if self.check >= 0 :
            idx = self.check
            dx = x - self.pre_pt[0]
            dy = y - self.pre_pt[1]

            if idx == 0:
                pts[0] = (x, y)
                pts[1][1] += dy
                pts[3][0] += dx

            if idx == 1:
                pts[1] = (x, y)
                pts[0][1] += dy
                pts[2][0] += dx

            if idx == 2:
                pts[2] = (x, y)
                pts[1][0] += dx
                pts[3][1] += dy

            if idx == 3:
                pts[3] = (x, y)
                pts[0][0] += dx
                pts[2][1] += dy
            
            self.pre_pt = (x, y)
            self.draw_rect(blured_img_sticker.copy(), img_sticker,  pts, small, title)

    ###############################
    # 이미지 미세 작업(fine) 관련 함수
    ###############################
    def onMouse_Fine(self, event, x, y, flags, param):
        self.param = param
        title = param['title']
        sub_title = param['sub_title']
        img_sticker = param['img_sticker']
        original_img_sticker = param['original_img_sticker']
        before_nukki_sticker = param['before_nukki_sticker']
        h, w = original_img_sticker.shape[:2]
        H, W = img_sticker.shape[:2]
        p_size = param['p_size']
            
        if event == cv2.EVENT_MOUSEMOVE:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                cv2.circle(img_sticker, (x, y), p_size, (0, 0, 0), -1)
                y1 = max(0, y-50)
                y2 = min(H, y+50)
                x1 = max(0, x-50)
                x2 = min(W, x+50)
                fine_work = img_sticker[y1:y2, x1:x2]
                fine_work = cv2.resize(fine_work, (W, H))
                
                cv2.imshow(title, img_sticker)
                cv2.imshow(sub_title, fine_work)
            
            if flags & cv2.EVENT_FLAG_RBUTTON:
                if before_nukki_sticker is not None:
                    y1 = max(0, y-p_size)
                    y2 = min(H, y+p_size)
                    x1 = max(0, x-p_size)
                    x2 = min(W, x+p_size)
                    img_sticker[y1:y2, x1:x2] = before_nukki_sticker[y1:y2, x1:x2]
                    
                    y1 = max(0, y-50)
                    y2 = min(H, y+50)
                    x1 = max(0, x-50)
                    x2 = min(W, x+50)
                    fine_work = img_sticker[y1:y2, x1:x2]
                    fine_work = cv2.resize(fine_work, (W, H))

                    cv2.imshow(title, img_sticker)
                    cv2.imshow(sub_title, fine_work)


        if event == cv2.EVENT_LBUTTONUP:
            self.fine_stack.append(img_sticker.copy())
            self.param['pos'] = (x, y)
            param['original_img_sticker'] = cv2.resize(img_sticker, (w, h))

        if event == cv2.EVENT_RBUTTONUP:
            self.fine_stack.append(img_sticker.copy())
            self.param['pos'] = (x, y)
            param['original_img_sticker'] = cv2.resize(img_sticker, (w, h))

        if event == cv2.EVENT_MOUSEWHEEL:
            if self.param == None:
                return
            
            MIN_SIZE = 3
            MAX_SIZE = 50
        
            p_size = p_size + 2 if flags > 0 else p_size - 2
            p_size = max(MIN_SIZE, min(MAX_SIZE, p_size))
            param['p_size'] = p_size