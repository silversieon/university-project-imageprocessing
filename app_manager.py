class AppManager:
    def __init__(self):
        from model.processor import MainProcessor
        self.current_view = None
        self.current_controller = None
        self.main_processor = MainProcessor()

    def show_start_screen(self):
        from view.start_view import StartView
        from controller.controller import StartController

        self.current_view = StartView()
        self.current_controller = StartController(self.current_view, self)
        self.current_view.show()
        self.current_view.center()

    def show_take_picture_screen(self):
        from view.take_picture_view import TakePictureView
        from model.processor import TakePictureProcessor
        from controller.controller import TakePictureController

        self.take_picture_processor = TakePictureProcessor()
        self.current_view = TakePictureView()
        self.current_controller = TakePictureController(self.current_view, self.take_picture_processor, self.main_processor, self)
        self.current_view.show()
        self.current_view.center()

    def show_basic_setting_screen(self):
        from view.basic_setting_view import BasicSettingView
        from controller.controller import BasicSettingController

        self.current_view = BasicSettingView(self.main_processor)
        self.current_controller = BasicSettingController(self.current_view, self.main_processor, self)
        self.current_view.show()
        self.current_view.center()