import logging
import os
import time

import gphoto2 as gp
from tqdm import tqdm


class Camera:
    def __init__(self, save_path):
        self.save_path = save_path
        self.timeout = 10000  # miliseconds
        self.is_capture = False
        self.camera = None

    def connect(self):
        self.camera = gp.Camera()
        self.camera.init()

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
            camera_model = ''
        return camera_model

    def capture(self):
        self.is_capture = True
        # 拍照
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        camera_file = self.camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)  # jpg
        # 文件名
        timestamp = str(round(time.time() * 1000))
        target = os.path.join(self.save_path, 'capture_{}{}'.format(timestamp, os.path.splitext(file_path.name)[-1]))
        camera_file.save(target)
        self.is_capture = False

    def bulb(self, speed):
        self.is_capture = True
        config = self.camera.get_config()
        # 设置为b门
        shutterspeed_config = config.get_child_by_name('shutterspeed')
        shutterspeed_config.set_value('Bulb')
        self.camera.set_config(config)
        # 开始曝光
        bulb_config = config.get_child_by_name('bulb')
        bulb_config.set_value(1)
        self.camera.set_config(config)
        time.sleep(speed + 1)
        # 结束曝光
        bulb_config.set_value(0)
        self.camera.set_config(config)
        basename = '{}_{}s'.format(time.strftime("%H%M%S", time.localtime()), speed)
        self.wait_for_event(basename, wait=10)
        self.is_capture = False

    def wait_for_event(self, basename, wait=10):
        before = time.time()
        after = before
        while after - before < wait:
            event_type, event_data = self.camera.wait_for_event(self.timeout)
            if event_type == gp.GP_EVENT_UNKNOWN:
                logging.debug('GP_EVENT_UNKNOWN')
                pass
            elif event_type == gp.GP_EVENT_TIMEOUT:
                logging.debug('GP_EVENT_TIMEOUT')
                pass
            elif event_type == gp.GP_EVENT_FILE_ADDED:  # 有文件生成
                logging.debug('GP_EVENT_FILE_ADDED')
                camera_file = self.camera.file_get(event_data.folder, event_data.name, gp.GP_FILE_TYPE_NORMAL)
                target = os.path.join(self.save_path, '{}{}'.format(basename, os.path.splitext(event_data.name)[-1]))
                camera_file.save(target)
                tqdm.write('获取照片, 保存到 {}'.format(target))
                pass
            elif event_type == gp.GP_EVENT_FOLDER_ADDED:
                logging.debug('GP_EVENT_FOLDER_ADDED')
                pass
            elif event_type == gp.GP_EVENT_CAPTURE_COMPLETE:
                logging.debug('GP_EVENT_CAPTURE_COMPLETE')
                pass
            after = time.time()

    def stop_blub(self):
        if self.is_capture:
            config = self.camera.get_config()
            bulb_config = config.get_child_by_name('bulb')
            bulb_config.set_value(0)
            self.camera.set_config(config)
            self.wait_for_event(basename='discard', wait=10)

    def disconnect(self):
        self.stop_blub()
        # 断开连接
        self.camera.exit()
