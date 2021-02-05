import sys
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QTextOption
from PyQt5.QtWidgets import QApplication

from shutter_qt5 import Ui_MainWindow


class ShutterWindows(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ShutterWindows, self).__init__()
        self.setupUi(self)
        second = 1000
        self.exposure_time = {
            '1/100s': int(second / 100),
            '1/10s': int(second / 10),
            '1s': second,
            '3s': second * 3,
            '5s': second * 5,
            '10s': second * 10,
            '15s': second * 15,
            '30s': second * 30,
            '1min': second * 60,
            '1min30s': second * 90,
            '2min': second * 120,
            '2min30s': second * 150,
            '3min': second * 180,
            '5min': second * 300
        }
        self.cb_exposure.addItems(self.exposure_time.keys())
        self.sp_num.setMinimum(1)
        self.tb_log.setWordWrapMode(QTextOption.NoWrap)
        self.btn_start.clicked.connect(self.on_start_click)
        self.action_connect.triggered.connect(self.on_action_connect)
        self.is_connect = False
        self.is_capturing = False

    def on_start_click(self):
        if not self.is_capturing:
            self.btn_start.setText("停止拍摄")
            self.output("开始拍摄", QColor('red'))
        else:
            self.btn_start.setText("开始拍摄")
            self.output("停止拍摄")
        self.is_capturing = not self.is_capturing

    def on_action_connect(self):
        if not self.is_connect:
            self.action_connect.setText("断开连接")
        else:
            self.action_connect.setText("连接设备")
        self.is_connect = not self.is_connect

    def output(self, text, color=QColor('black')):
        time = datetime.now().strftime("%H:%M:%S")
        self.tb_log.setTextColor(color)
        self.tb_log.append('{}: {}'.format(time, text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = ShutterWindows()
    MainWindow.show()
    sys.exit(app.exec_())
