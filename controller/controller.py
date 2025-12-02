from PyQt5.QtCore import QCoreApplication
from model.settings import Settings

####################
# 1. 시작 컨트롤러
####################
class StartController:
    def __init__(self, view, app_manager):
        # 시작 컨트롤러의 view와 app_manager 정의
        self.view = view
        self.app_manager = app_manager

        # view의 버튼 클릭시 이벤트 처리
        self.view.start_btn.clicked.connect(self.on_start_clicked)
        self.view.quit_btn.clicked.connect(QCoreApplication.instance().quit)

    # app_manager의 다음 화면 출력 함수 호출
    def on_start_clicked(self):
        self.app_manager.show_take_picture_screen()

####################
# 2. 사진 촬영 컨트롤러
####################
class TakePictureController:
    def __init__(self, view, processor, main_processor, app_manager):
        # 이미지 촬영 컨트롤러의 view, processor, app_manager 정의
        self.view = view
        self.take_picture_processor = processor
        self.main_processor = main_processor
        self.app_manager = app_manager

        # view의 버튼 클릭시 이벤트 처리
        self.view.capture_btn.clicked.connect(self.on_capture_clicked)
        self.view.c.time_out.connect(self.on_capture_clicked)
    
    def on_capture_clicked(self):
        ret, frame = self.view.video.read()
        if ret:
            captured_image = self.take_picture_processor.take_picture(frame)
            count = self.main_processor.save_images(captured_image)
            self.view.isCapturing = True
            self.view.capture_count.setText(f"{count} / 4")
            self.view.current_sec = Settings.CAMERA_TIME + 1
            self.view.second_count.setStyleSheet("background-color: rgb(255, 255, 255); color: black; font-size: 60px; font-weight: bold;")
            if(count == 4): self.app_manager.show_basic_setting_screen()

####################
# 3. 기본 설정 컨트롤러
####################
class BasicSettingController:
    def __init__(self, view, main_processor, app_manager):
        # 이미지 기본 설정 컨트롤러의 view, processor, app_manager 정의
        self.view = view
        self.main_processor = main_processor
        self.app_manager = app_manager

        # view의 버튼 클릭시 이벤트 처리
        self.view.next_btn.clicked.connect(self.on_next_clicked)
        self.view.color_btn.clicked.connect(self.on_color_clicked)
        self.view.gray_btn.clicked.connect(self.on_gray_clicked)
        self.view.flip_btn.clicked.connect(self.on_flip_clicked)

        for i, btn in enumerate(self.view.color_palette_btn):
            btn.clicked.connect(lambda checked, idx=i: self.on_color_palette_clicked(idx))

        for i, btn in enumerate(self.view.special_frame_btn):
            btn.clicked.connect(lambda checked, idx=i: self.on_special_frame_clicked(idx))

        self.view.retry_btn.clicked.connect(self.on_retry_clicked)

    def on_next_clicked(self):
        self.app_manager.show_img_sticker_setting_screen()

    def on_color_clicked(self):
        four_cut = self.main_processor.convert_to_color()
        self.view.update_main_area(four_cut)

    def on_gray_clicked(self):
        four_cut = self.main_processor.convert_to_gray()
        self.view.update_main_area(four_cut)
    
    def on_flip_clicked(self):
        four_cut = self.main_processor.flip_captured_images()
        self.view.update_main_area(four_cut)

    def on_color_palette_clicked(self, idx):
        four_cut = self.main_processor.change_background_color(idx)
        self.view.update_main_area(four_cut)

    def on_special_frame_clicked(self, idx):
        four_cut = self.main_processor.change_background_special(idx)
        self.view.update_main_area(four_cut)

    def on_retry_clicked(self):
        self.view.close()
        self.main_processor.reset()
        self.app_manager.show_take_picture_screen()

########################
# 4. 이미지 스티커 컨트롤러
########################
class ImgStickerSettingController():
    def __init__(self, view, main_processor, app_manager):
        # 이미지 스티커 설정 컨트롤러의 view, processor, app_manager 정의
        self.view = view
        self.main_processor = main_processor
        self.app_manager = app_manager

        # view의 버튼 클릭시 이벤트 처리
        self.view.next_btn.clicked.connect(self.on_next_clicked)
        self.view.img_load_btn.clicked.connect(self.on_img_load_clicked)
        self.view.img_sticker_btn.clicked.connect(self.on_img_sticker_btn_clicked)
        self.view.crop_btn.clicked.connect(self.on_crop_clicked)
        self.view.nukki_btn.clicked.connect(self.on_nukki_clicked)
        self.view.fine_btn.clicked.connect(self.on_fine_clicked)
        self.view.undo_btn.clicked.connect(self.on_undo_clicked)
        self.view.redo_btn.clicked.connect(self.on_redo_clicked)

    def on_next_clicked(self):
        self.main_processor.util_processor.reset()
        self.app_manager.show_emoji_sticker_setting_screen()
    
    def on_img_load_clicked(self):
        loaded_img = self.main_processor.load_img()
        if loaded_img is not None:
            self.view.set_img_sticker_btn(loaded_img)
        
    def on_crop_clicked(self):
        cropped_img = self.main_processor.cut_img()
        if cropped_img is not None:
            self.view.set_img_sticker_btn(cropped_img)

    def on_nukki_clicked(self):
        nukkied_img = self.main_processor.nukki_img()
        if nukkied_img is not None:
            self.view.set_img_sticker_btn(nukkied_img)

    def on_fine_clicked(self):
        fined_img = self.main_processor.fine_img()
        if fined_img is not None:
            self.view.set_img_sticker_btn(fined_img)

    def on_img_sticker_btn_clicked(self):
        four_cut = self.main_processor.add_img()
        if four_cut is not None:
            self.view.update_main_area(four_cut)
    
    def on_undo_clicked(self):
        four_cut = self.main_processor.undo_four_cut()
        self.view.update_main_area(four_cut)

    def on_redo_clicked(self):
        four_cut = self.main_processor.redo_four_cut()
        self.view.update_main_area(four_cut)

########################
# 5. 이모지 스티커 컨트롤러
########################
class EmojiStickerSettingController:
    def __init__(self, view, main_processor, app_manager):
        # 이모지 스티커 설정 컨트롤러의 view, processor, app_manager 정의
        self.view = view
        self.main_processor = main_processor
        self.app_manager = app_manager

        # view의 버튼 클릭시 이벤트 처리
        self.view.save_btn.clicked.connect(self.on_save_clicked)
        self.view.text_btn.clicked.connect(self.on_text_clicked)
        self.view.undo_btn.clicked.connect(self.on_undo_clicked)
        self.view.redo_btn.clicked.connect(self.on_redo_clicked)
        for i, btn in enumerate(self.view.emoji_btn):
            btn.clicked.connect(lambda checked, idx=i: self.on_emoji_btn_clicked(idx))

    def on_save_clicked(self):
        self.main_processor.save_completed_four_cut()
        self.main_processor.reset()
        self.app_manager.show_start_screen()

    def on_text_clicked(self):
        four_cut = self.main_processor.add_text(self.view.input.text())
        self.view.update_main_area(four_cut)

    def on_undo_clicked(self):
        four_cut = self.main_processor.undo_four_cut()
        self.view.update_main_area(four_cut)

    def on_redo_clicked(self):
        four_cut = self.main_processor.redo_four_cut()
        self.view.update_main_area(four_cut)

    def on_emoji_btn_clicked(self, idx):
        four_cut = self.main_processor.add_emoji(idx)
        self.view.update_main_area(four_cut)