import logging
import sys
from datetime import datetime
from enum import Enum

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from camera import Camera, CameraError, CameraEvent
from config import Config
from shutter_qt5 import Ui_MainWindow

logging.basicConfig(level=logging.DEBUG, filename='shutter.log', format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

bulb_exposure_time = {
    '1min': 1000 * 60, '1min30s': 1000 * 90, '2min': 1000 * 120, '2min30s': 1000 * 150,
    '3min': 1000 * 180, '5min': 1000 * 300, '6min': 1000 * 360, '8min': 1000 * 480,
    '10min': 1000 * 600
}
exposure_time = {
    '0.4s': ('4/10', '400.0'), '0.5s': ('5/10', '500.0'), '0.6s': ('6/10', '600.0'),
    '0.8s': ('8/10', '800.0'), '1s': ('10/10', '1000.0'), '1.3s': ('13/10', '1300.0'),
    '1.6s': ('16/10', '1600.0'), '2s': ('20/10', '2000.0'), '2.5s': ('25/10', '2500.0'),
    '3.2s': ('32/10', '3200.0'), '4s': ('40/10', '4000.0'), '5s': ('50/10', '5000.0'),
    '6s': ('60/10', '6000.0'), '8s': ('80/10', '8000.0'), '10s': ('100/10', '10000.0'),
    '13s': ('130/10', '13000.0'), '15s': ('150/10', '15000.0'), '20s': ('200/10', '20000.0'),
    '25s': ('250/10', '25000.0'), '30s': ('300/10', '30000.0')
}


class UiEvent(Enum):
    ON_DEVICE_CONNECT = 1
    ON_DEVICE_DISCONNECT = 2
    ON_CHECK_EVENT_START = 3
    ON_CHECK_EVENT_FINISH = 4
    ON_CAPTURE_START = 5
    ON_CAPTURE_FINISH = 6
    ON_BULB_CHECKED = 7
    ON_BULB_NOT_CHECKED = 8


class ShutterWindows(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(ShutterWindows, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.sp_num.setMinimum(1)
        self.cbl_exposure.addItems(exposure_time.keys())
        self.tb_log.document().setMaximumBlockCount(300)

        self.is_connect = False
        self.is_capturing = False
        self.is_checking_event = False
        self.camera_model = ''
        self.capture_t = None
        self.wait_for_event_t = None
        # 点击事件
        self.btn_start.clicked.connect(self.on_start_click)
        self.btn_check_event.clicked.connect(self.on_check_event_clicked)
        self.action_connect.triggered.connect(self.on_action_connect_clicked)
        self.action_save_dir.triggered.connect(self.on_action_save_dir_clicked)
        self.cb_bulb.stateChanged.connect(self.on_blub_state_change)
        self.camera = Camera(Config.output_dir)

    def update_element(self, ui_event):
        """ 更新ui """
        if ui_event == UiEvent.ON_DEVICE_CONNECT:
            self.action_connect.setText("断开连接")
            self.btn_check_event.setEnabled(True)
            self.btn_start.setEnabled(True)
        elif ui_event == UiEvent.ON_DEVICE_DISCONNECT:
            self.action_connect.setText("连接设备")
            self.btn_check_event.setEnabled(False)
            self.btn_start.setEnabled(False)
        elif ui_event == UiEvent.ON_CAPTURE_START:
            self.btn_start.setText("停止拍摄")
            self.btn_check_event.setEnabled(False)
            self.cb_bulb.setEnabled(False)
            self.cbl_exposure.setEnabled(False)
            self.sp_num.setEnabled(False)
            self.pb_all.setValue(0)
            self.tl_progress.setText('{}/{}'.format(0, self.sp_num.value()))
            if not self.cb_bulb.isChecked():  # 普通模式
                self.pb_single.setMaximum(0)
            else:  # b门模式
                self.pb_single.setMaximum(100)
                self.pb_single.setValue(0)
        elif ui_event == UiEvent.ON_CAPTURE_FINISH:
            self.btn_start.setText("开始拍摄")
            self.btn_start.setEnabled(True)
            self.btn_check_event.setEnabled(True)
            self.cb_bulb.setEnabled(True)
            self.cbl_exposure.setEnabled(True)
            self.sp_num.setEnabled(True)
            self.pb_single.setMaximum(100)
            self.pb_single.setValue(0)
        elif ui_event == UiEvent.ON_CHECK_EVENT_START:
            self.btn_check_event.setText("停止检查")
            self.btn_start.setEnabled(False)
        elif ui_event == UiEvent.ON_CHECK_EVENT_FINISH:
            self.btn_check_event.setText("检查事件")
            self.btn_start.setEnabled(True)
        elif ui_event == UiEvent.ON_BULB_CHECKED:
            self.cbl_exposure.clear()
            self.cbl_exposure.addItems(bulb_exposure_time.keys())
        elif ui_event == UiEvent.ON_BULB_NOT_CHECKED:
            self.cbl_exposure.clear()
            self.cbl_exposure.addItems(exposure_time.keys())

    def on_start_click(self):
        """ 点击开始拍摄按钮 """
        if not self.is_capturing:
            num = self.sp_num.value()
            if not self.cb_bulb.isChecked():  # 普通模式
                self.capture_t = CaptureThread(self.camera, False, exposure_time[self.cbl_exposure.currentText()][0], num)
            else:
                self.capture_t = CaptureThread(self.camera, True, bulb_exposure_time[self.cbl_exposure.currentText()], num)
            self.capture_t.start()
            self.capture_t.progress_update.connect(self.update_progress_bar)
            self.capture_t.picture_output.connect(self.picture_output)
            self.capture_t.complete.connect(self.shoot_complete)
            self.capture_t.error.connect(self.shoot_error)

            self.update_element(UiEvent.ON_CAPTURE_START)
            self.is_capturing = True
            self.log_output("开始拍摄")
        else:
            self.capture_t.stop()
            self.btn_start.setEnabled(False)

    def on_check_event_clicked(self):
        """ 点击检查事件按钮 """
        if not self.is_checking_event:  # 检查事件
            # 启动线程
            self.wait_for_event_t = WaitForEventThread(self.camera)
            self.wait_for_event_t.start()
            self.wait_for_event_t.event.connect(self.camera_event_listener)
            self.update_element(UiEvent.ON_CHECK_EVENT_START)
            self.is_checking_event = True
        else:
            self.camera.stop_wait_for_event()
            self.update_element(UiEvent.ON_CHECK_EVENT_FINISH)
            self.is_checking_event = False

    def on_action_connect_clicked(self):
        """ 点击连接设备菜单 """
        if not self.is_connect:  # 连接设备
            try:
                self.camera.connect()
                self.camera_model = self.camera.get_camera_model()
                self.log_output('{} 已连接'.format(self.camera_model))
                self.update_element(UiEvent.ON_DEVICE_CONNECT)
                self.is_connect = True
            except CameraError as e:
                self.log_output('连接设备遇到问题: {}'.format(e), QColor('red'))
                return
        else:  # 断开设备
            if self.is_capturing or self.is_checking_event:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('请先停止任务')
                msg.setWindowTitle("Error")
                msg.exec_()
            else:
                self.camera.disconnect()
                self.log_output('{} 断开连接'.format(self.camera_model))
                self.update_element(UiEvent.ON_DEVICE_DISCONNECT)
                self.is_connect = False

    def on_action_save_dir_clicked(self):
        """ 选择文件夹 """
        directory = QFileDialog.getExistingDirectory(self, '选择文件夹', Config.output_dir)
        if len(directory) > 0:
            Config.set_output_dir(directory)
            self.camera.set_output_dir(directory)

    def on_blub_state_change(self):
        """ 当B门被选中时触发 """
        if self.cb_bulb.isChecked():
            self.update_element(UiEvent.ON_BULB_CHECKED)
        else:
            self.update_element(UiEvent.ON_BULB_NOT_CHECKED)

    def log_output(self, text, color=QColor('black')):
        """ 输出到log """
        time = datetime.now().strftime("%H:%M:%S")
        self.tb_log.setTextColor(color)
        self.tb_log.append('{} {}'.format(time, text))

    def update_progress_bar(self, single_value, value):
        """ 更新进度条 """
        self.pb_single.setValue(single_value)
        self.pb_all.setValue(int((value / self.sp_num.value()) * 100))
        self.tl_progress.setText('{}/{}'.format(value, self.sp_num.value()))

    def picture_output(self, pics):
        """ 输出照片 """
        for path in pics:
            self.log_output('{} -> 保存相片到 {}'.format(self.camera_model, path))

    def shoot_complete(self):
        """ 拍摄完成 """
        self.update_element(UiEvent.ON_CAPTURE_FINISH)
        self.is_capturing = False
        self.log_output("拍摄结束")

    def shoot_error(self, message):
        """ 拍摄错误 """
        self.update_element(UiEvent.ON_CAPTURE_FINISH)
        self.is_capturing = False
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def camera_event_listener(self, event_type, info=None):
        """ 相机事件监听 """
        if event_type == CameraEvent.EVENT_UNKNOWN:
            pass
            # self.output('{} -> EVENT_UNKNOWN'.format(self.camera_model))
        elif event_type == CameraEvent.EVENT_TIMEOUT:
            pass
            # self.output('{} -> EVENT_TIMEOUT'.format(self.camera_model))
        elif event_type == CameraEvent.EVENT_FILE_ADDED:  # 有文件生成
            self.log_output('{} -> 保存相片到 {}'.format(self.camera_model, info))
        elif event_type == CameraEvent.EVENT_FOLDER_ADDED:
            self.log_output('{} -> EVENT_FOLDER_ADDED'.format(self.camera_model))
        elif event_type == CameraEvent.EVENT_CAPTURE_COMPLETE:
            self.log_output('{} -> EVENT_CAPTURE_COMPLETE'.format(self.camera_model))


class WaitForEventThread(QThread):
    event = pyqtSignal(int, str)

    def __init__(self, camera: Camera):
        super(WaitForEventThread, self).__init__()
        self.camera = camera

    def run(self) -> None:
        self.camera.wait_for_event_forever(self.event.emit)


class CaptureThread(QThread):
    picture_output = pyqtSignal(list)
    progress_update = pyqtSignal(int, int)
    complete = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, camera: Camera, is_bulb: bool, shutterspeed, num: int):
        super(CaptureThread, self).__init__()
        self.camera = camera
        self.is_bulb = is_bulb
        self.shutterspeed = shutterspeed
        self.num = num
        self.working = True

    def run(self) -> None:
        if not self.is_bulb:  # 普通模式
            self.camera.set_shutterspeed(self.shutterspeed)
            for i in range(self.num):
                if not self.working:
                    break
                pics = self.camera.capture()
                self.picture_output.emit(pics)
                self.progress_update.emit(0, i + 1)
        else:  # b门模式
            if self.camera.get_shutterspeed() != 'Bulb':
                self.error.emit('请设置为bulb模式')
            else:
                for i in range(self.num):
                    if not self.working:
                        break
                    self.camera.bulb()
                    seconds = int(self.shutterspeed / 1000)
                    for j in range(seconds):
                        if not self.working:
                            break
                        self.sleep(1)
                        self.progress_update.emit(int(j / seconds * 100), i)
                    pics = self.camera.blub_stop()
                    self.picture_output.emit(pics)
                    self.progress_update.emit(100, i + 1)
        self.complete.emit()

    def stop(self):
        self.working = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = ShutterWindows()
    MainWindow.show()
    sys.exit(app.exec_())
