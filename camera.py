import os
import time
import uuid
from enum import Enum, auto

import gphoto2 as gp


class CameraError(Exception):
    pass


class CameraEvent(Enum):
    EVENT_UNKNOWN = auto()
    EVENT_TIMEOUT = auto()
    EVENT_FILE_ADDED = auto()
    EVENT_FOLDER_ADDED = auto()
    EVENT_CAPTURE_COMPLETE = auto()
    EVENT_FINISH = auto()


class Camera:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.camera = None
        self.wait_event_loop = False

    def set_output_dir(self, path):
        self.output_dir = path

    def connect(self):
        try:
            self.camera = gp.Camera()
            self.camera.init()
        except gp.GPhoto2Error as e:
            raise CameraError(str(e))

    def get_camera_model(self):
        camera_config = self.camera.get_config()
        # get the camera model
        OK, camera_model = gp.gp_widget_get_child_by_name(
            camera_config, 'cameramodel')
        if OK < gp.GP_OK:
            OK, camera_model = gp.gp_widget_get_child_by_name(
                camera_config, 'model')
        if OK >= gp.GP_OK:
            camera_model = camera_model.get_value()
        else:
            camera_model = 'unknown model'
        return camera_model

    def wait_for_event_forever(self, listener):
        self.wait_event_loop = True
        while self.wait_event_loop:
            event_type, event_data = self.camera.wait_for_event(1000)
            if event_type == gp.GP_EVENT_UNKNOWN:
                listener(CameraEvent.EVENT_UNKNOWN, event_data)
            elif event_type == gp.GP_EVENT_TIMEOUT:
                listener(CameraEvent.EVENT_TIMEOUT, event_data)
            elif event_type == gp.GP_EVENT_FILE_ADDED:  # 有文件生成
                file_name = '{}_{}'.format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()), uuid.uuid4().hex)  # 生成文件名
                target = self._save_file(event_data.folder, event_data.name, file_name)
                listener(CameraEvent.EVENT_FILE_ADDED, target)
            elif event_type == gp.GP_EVENT_FOLDER_ADDED:
                listener(CameraEvent.EVENT_FOLDER_ADDED, event_data)
            elif event_type == gp.GP_EVENT_CAPTURE_COMPLETE:
                listener(CameraEvent.EVENT_CAPTURE_COMPLETE, event_data)
        listener(CameraEvent.EVENT_FINISH, None)

    def stop_wait_for_event(self):
        self.wait_event_loop = False

    def set_shutterspeed(self, shutterspeed):
        config = self.camera.get_config()
        shutterspeed_config = config.get_child_by_name('shutterspeed')
        shutterspeed_config.set_value(shutterspeed)
        self.camera.set_config(config)

    def get_shutterspeed(self):
        config = self.camera.get_config()
        shutterspeed_config = config.get_child_by_name('shutterspeed')
        return shutterspeed_config.get_value()

    def capture(self, listener):
        # 拍照
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        listener(CameraEvent.EVENT_CAPTURE_COMPLETE, None)
        file_name = '{}_{}'.format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()), uuid.uuid4().hex)  # 生成文件名
        jpg = self._save_file(file_path.folder, file_path.name, file_name)  # 保存jpg
        listener(CameraEvent.EVENT_FILE_ADDED, jpg)
        files = self.wait_for_save(file_name, listener=listener)  # 保存raw
        files.insert(0, jpg)
        listener(CameraEvent.EVENT_FINISH, None)
        return files

    # 等待保存事件, 单位: 秒
    def wait_for_save(self, save_name, listener=None, timeout=10):
        before = time.time()
        after = before
        targets = []
        while after - before < timeout:
            event_type, event_data = self.camera.wait_for_event(500)
            if event_type == gp.GP_EVENT_FILE_ADDED:  # 有文件生成
                target = self._save_file(event_data.folder, event_data.name, save_name)
                targets.append(target)
                if listener is not None:
                    listener(CameraEvent.EVENT_FILE_ADDED, target)
            after = time.time()
        return targets

    # 保存图片
    def _save_file(self, folder, name, save_name):
        camera_file = self.camera.file_get(folder, name, gp.GP_FILE_TYPE_NORMAL)  # 获取照片
        ext = os.path.splitext(name)[-1]
        target = os.path.join(self.output_dir, '{}{}'.format(save_name, ext))
        camera_file.save(target)  # 存储
        return target

    def set_bulb(self):
        config = self.camera.get_config()
        shutterspeed_config = config.get_child_by_name('shutterspeed')
        shutterspeed_config.set_value('Bulb')
        self.camera.set_config(config)

    def bulb(self):
        # 开始曝光
        config = self.camera.get_config()
        bulb_config = config.get_child_by_name('bulb')
        bulb_config.set_value(1)
        self.camera.set_config(config)

    def blub_stop(self, listener):
        config = self.camera.get_config()
        bulb_config = config.get_child_by_name('bulb')
        bulb_config.set_value(0)
        self.camera.set_config(config)
        listener(CameraEvent.EVENT_CAPTURE_COMPLETE, None)
        file_name = '{}_{}'.format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()), uuid.uuid4().hex)  # 生成文件名
        files = self.wait_for_save(file_name, listener)
        listener(CameraEvent.EVENT_FINISH, None)
        return files

    # 断开连接
    def disconnect(self):
        self.camera.exit()
