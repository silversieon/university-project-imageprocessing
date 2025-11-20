from PyQt5.QtCore import QCoreApplication

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

class TakePictureController:
    def __init__(self, view, processor, main_processor, app_manager):
        # 이미지 촬영 컨트롤러의 view, processor, app_manager 정의
        self.view = view
        self.take_picture_processor = processor
        self.main_processor = main_processor
        self.app_manager = app_manager

        # view의 버튼 클릭시 이벤트 처리
        self.view.capture_btn.clicked.connect(self.on_capture_clicked)
    
    def on_capture_clicked(self):
        ret, frame = self.view.video.read()
        if ret:
            captured_image = self.take_picture_processor.take_picture(frame)
            count = self.main_processor.save_images(captured_image)
            if(count == 4): self.app_manager.show_basic_setting_screen()

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

    def on_next_clicked(self):
        self.main_processor.save_completed_four_cut()

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