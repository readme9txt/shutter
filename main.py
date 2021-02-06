import logging
import os
import sys
from datetime import datetime
from threading import Thread

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QApplication

from camera import Camera, CameraError
from shutter_qt5 import Ui_MainWindow

logging.basicConfig(level=logging.DEBUG, filename='shutter.log', format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class ShutterWindows(QtWidgets.QMainWindow, Ui_MainWindow):
    bulb_exposure_time = {
        '1min': 1000 * 60, '1min30s': 1000 * 90, '2min': 1000 * 120, '2min30s': 1000 * 150,
        '3min': 1000 * 180, '5min': 1000 * 300, '6min': 1000 * 360, '8min': 1000 * 480,
        '10min': 1000 * 600
    }
    exposure_time = {
        '0.4s': '4/10', '0.5s': '5/10', '0.6s': '6/10', '0.8s': '8/10',
        '1s': '10/10', '1.3s': '13/10', '1.6s': '16/10', '2s': '20/10',
        '2.5s': '25/10', '3.2s': '32/10', '4s': '40/10', '5s': '50/10',
        '6s': '60/10', '8s': '80/10', '10s': '100/10', '13s': '130/10',
        '15s': '150/10', '20s': '200/10', '25s': '250/10', '30s': '300/10'
    }

    def __init__(self):
        super(ShutterWindows, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.sp_num.setMinimum(1)
        self.cbl_exposure.addItems(self.exposure_time.keys())
        self.tb_log.document().setMaximumBlockCount(300)

        self.is_connect = False
        self.is_capturing = False
        self.is_checking_event = False
        self.camera_model = ''
        # 点击事件
        self.btn_start.clicked.connect(self.on_start_click)
        self.btn_check_event.clicked.connect(self.on_check_event_clicked)
        self.action_connect.triggered.connect(self.on_action_connect)
        self.cb_bulb.stateChanged.connect(self.on_blub_state_change)
        self.camera = Camera(os.getcwd())

    def on_start_click(self):
        if not self.is_capturing:
            self.btn_start.setText("停止拍摄")
            self.output("开始拍摄", QColor('red'))
            self.is_capturing = True
        else:
            self.btn_start.setText("开始拍摄")
            self.output("停止拍摄")
            self.is_capturing = False

    def on_check_event_clicked(self):
        if not self.is_checking_event:  # 检查事件
            self.t = WorkThread(self.camera)
            self.t.start()
            self.t.log_output.connect(self.event_listener)
            self.btn_check_event.setText("停止检查")
            self.btn_start.setEnabled(False)
            self.is_checking_event = True
        else:
            self.camera.stop_wait_for_event()
            self.btn_check_event.setText("检查事件")
            self.btn_start.setEnabled(True)
            self.is_checking_event = False

    def event_listener(self, event_type, info=None):
        if event_type == Camera.EVENT_UNKNOWN:
            pass
            # self.output('{} -> EVENT_UNKNOWN'.format(self.camera_model))
        elif event_type == Camera.EVENT_TIMEOUT:
            pass
            # self.output('{} -> EVENT_TIMEOUT'.format(self.camera_model))
        elif event_type == Camera.EVENT_FILE_ADDED:  # 有文件生成
            self.output('{} -> 保存相片到 {}'.format(self.camera_model, info))
        elif event_type == Camera.EVENT_FOLDER_ADDED:
            self.output('{} -> EVENT_FOLDER_ADDED'.format(self.camera_model))
        elif event_type == Camera.EVENT_CAPTURE_COMPLETE:
            self.output('{} -> EVENT_CAPTURE_COMPLETE'.format(self.camera_model))

    def on_action_connect(self):
        if not self.is_connect:  # 连接设备
            try:
                self.camera.connect()
                self.action_connect.setText("断开连接")
                self.camera_model = self.camera.get_camera_model()
                self.output('{} 已连接'.format(self.camera_model))
                self.btn_check_event.setEnabled(True)
                self.btn_start.setEnabled(True)
                self.is_connect = True
            except CameraError as e:
                self.output('连接设备遇到问题: {}'.format(e), QColor('red'))
                return
        else:  # 断开设备
            self.camera.disconnect()
            self.output('{} 断开连接'.format(self.camera_model))
            self.action_connect.setText("连接设备")
            self.btn_check_event.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.is_connect = False

    def on_blub_state_change(self):
        if self.cb_bulb.isChecked():
            self.cbl_exposure.clear()
            self.cbl_exposure.addItems(self.bulb_exposure_time.keys())
        else:
            self.cbl_exposure.clear()
            self.cbl_exposure.addItems(self.exposure_time.keys())

    def output(self, text, color=QColor('black')):
        time = datetime.now().strftime("%H:%M:%S")
        self.tb_log.setTextColor(color)
        self.tb_log.append('{} {}'.format(time, text))


class WorkThread(QThread):
    log_output = pyqtSignal(int, str)

    def __init__(self, camera: Camera):
        super(WorkThread, self).__init__()
        self.camera = camera

    def run(self) -> None:
        self.camera.wait_for_event_forever(self.log_output.emit)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = ShutterWindows()
    MainWindow.show()
    sys.exit(app.exec_())
