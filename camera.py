import os
import time
import uuid
from enum import Enum

import gphoto2 as gp


class CameraError(Exception):
    pass


class CameraEvent(Enum):
    EVENT_UNKNOWN = 1
    EVENT_TIMEOUT = 2
    EVENT_FILE_ADDED = 3
    EVENT_FOLDER_ADDED = 4
    EVENT_CAPTURE_COMPLETE = 5


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
                listener(CameraEvent.EVENT_UNKNOWN, None)
            elif event_type == gp.GP_EVENT_TIMEOUT:
                listener(CameraEvent.EVENT_TIMEOUT, None)
            elif event_type == gp.GP_EVENT_FILE_ADDED:  # 有文件生成
                target = self._save_file(event_data.folder, event_data.name)
                listener(CameraEvent.EVENT_FILE_ADDED, target)
            elif event_type == gp.GP_EVENT_FOLDER_ADDED:
                listener(CameraEvent.EVENT_FOLDER_ADDED, None)
            elif event_type == gp.GP_EVENT_CAPTURE_COMPLETE:
                listener(CameraEvent.EVENT_CAPTURE_COMPLETE, None)

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

    def capture(self):
        # 拍照
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        jpg = self._save_file(file_path.folder, file_path.name)  # 保存jpg
        files = self.wait_for_save()  # 保存raw
        files.insert(0, jpg)
        return files

    # 等待保存事件, 单位: 秒
    def wait_for_save(self, timeout=10):
        before = time.time()
        after = before
        targets = []
        while after - before < timeout:
            event_type, event_data = self.camera.wait_for_event(500)
            if event_type == gp.GP_EVENT_FILE_ADDED:  # 有文件生成
                target = self._save_file(event_data.folder, event_data.name)
                targets.append(target)
            after = time.time()
        return targets

    # 保存图片
    def _save_file(self, folder, name):
        camera_file = self.camera.file_get(folder, name, gp.GP_FILE_TYPE_NORMAL)  # 获取照片
        file_name = '{}_{}'.format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()), uuid.uuid4().hex)  # 生成文件名
        ext = os.path.splitext(name)[-1]
        target = os.path.join(self.output_dir, '{}{}'.format(file_name, ext))
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

    def blub_stop(self):
        config = self.camera.get_config()
        bulb_config = config.get_child_by_name('bulb')
        bulb_config.set_value(0)
        self.camera.set_config(config)
        return self.wait_for_save()

    # 断开连接
    def disconnect(self):
        self.camera.exit()
