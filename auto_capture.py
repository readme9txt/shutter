import argparse
import logging
import os
import signal
import sys
import time

import gphoto2 as gp
from tqdm import tqdm


class AutoCapture:
    def __init__(self, save_path):
        self.camera = gp.Camera()
        self.camera.init()
        self.save_path = save_path
        self.timeout = 10000  # miliseconds
        self.is_capture = False

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

    def disconnect(self):
        if self.is_capture:
            config = self.camera.get_config()
            bulb_config = config.get_child_by_name('bulb')
            bulb_config.set_value(0)
            self.camera.set_config(config)
            self.wait_for_event(basename='discard', wait=10)
        # 断开连接
        self.camera.exit()


def signal_handler(sig, frame):
    tqdm.write('断开连接')
    ac.disconnect()
    sys.exit(0)


if __name__ == '__main__':
    logging.basicConfig(filename='auto_capture.log', level=logging.WARNING, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    parse = argparse.ArgumentParser()
    parse.add_argument('-s', '--speed', type=int, required=True, help='Shutter speed')
    parse.add_argument('-n', '--num', type=int, required=True, help='Number of Shots')
    parse.add_argument('-d', '--dst_dir', type=str, default=sys.path[0], help='Save path')
    arguments = parse.parse_args(sys.argv[1:])

    # 保存路径
    dst_dir = '{}/{}'.format(arguments.dst_dir, time.strftime('%Y-%m-%d', time.localtime()))
    if not os.path.exists(dst_dir):
        original_umask = os.umask(0)
        os.mkdir(dst_dir, 0o777)
        os.umask(original_umask)

    signal.signal(signal.SIGINT, signal_handler)

    tqdm.write('曝光时间 {} s, 拍摄 {} 张, 存储路径 {}'.format(arguments.speed, arguments.num, dst_dir))
    ac = AutoCapture(dst_dir)
    tqdm.write('检查是否有未保存的照片..')
    ac.wait_for_event('discard', wait=5)
    for i in tqdm(range(arguments.num)):
        tqdm.write('正在拍摄第 {} 张...'.format(i + 1))
        ac.bulb(arguments.speed)
    ac.disconnect()
