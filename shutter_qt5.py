# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shutter_qt5.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import os

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(523, 268)
        MainWindow.setMinimumSize(QtCore.QSize(523, 268))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        current_path = os.path.abspath(os.path.dirname(__file__))
        icon.addPixmap(QtGui.QPixmap("{}/shutter.ico".format(current_path)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tb_log = QtWidgets.QTextBrowser(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.tb_log.setFont(font)
        self.tb_log.setAutoFillBackground(False)
        self.tb_log.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.tb_log.setObjectName("tb_log")
        self.verticalLayout.addWidget(self.tb_log)
        self.pb_single = QtWidgets.QProgressBar(self.centralwidget)
        self.pb_single.setMinimum(0)
        self.pb_single.setMaximum(100)
        self.pb_single.setProperty("value", 0)
        self.pb_single.setTextVisible(False)
        self.pb_single.setObjectName("pb_single")
        self.verticalLayout.addWidget(self.pb_single)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pb_all = QtWidgets.QProgressBar(self.centralwidget)
        self.pb_all.setProperty("value", 0)
        self.pb_all.setTextVisible(False)
        self.pb_all.setObjectName("pb_all")
        self.horizontalLayout_2.addWidget(self.pb_all)
        self.tl_progress = QtWidgets.QLabel(self.centralwidget)
        self.tl_progress.setObjectName("tl_progress")
        self.horizontalLayout_2.addWidget(self.tl_progress)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setMinimumSize(QtCore.QSize(170, 125))
        self.groupBox.setMaximumSize(QtCore.QSize(170, 125))
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.cb_bulb = QtWidgets.QCheckBox(self.groupBox)
        self.cb_bulb.setMinimumSize(QtCore.QSize(69, 20))
        self.cb_bulb.setMaximumSize(QtCore.QSize(69, 16777215))
        self.cb_bulb.setText("")
        self.cb_bulb.setCheckable(True)
        self.cb_bulb.setObjectName("cb_bulb")
        self.horizontalLayout_6.addWidget(self.cb_bulb, 0, QtCore.Qt.AlignVCenter)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.cbl_exposure = QtWidgets.QComboBox(self.groupBox)
        self.cbl_exposure.setMinimumSize(QtCore.QSize(69, 0))
        self.cbl_exposure.setMaximumSize(QtCore.QSize(69, 16777215))
        self.cbl_exposure.setObjectName("cbl_exposure")
        self.horizontalLayout_3.addWidget(self.cbl_exposure, 0, QtCore.Qt.AlignVCenter)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.sp_num = QtWidgets.QSpinBox(self.groupBox)
        self.sp_num.setMinimumSize(QtCore.QSize(69, 0))
        self.sp_num.setMaximumSize(QtCore.QSize(69, 16777215))
        self.sp_num.setObjectName("sp_num")
        self.horizontalLayout_4.addWidget(self.sp_num, 0, QtCore.Qt.AlignVCenter)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(170, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.btn_check_event = QtWidgets.QPushButton(self.centralwidget)
        self.btn_check_event.setEnabled(False)
        self.btn_check_event.setObjectName("btn_check_event")
        self.verticalLayout_2.addWidget(self.btn_check_event)
        self.btn_start = QtWidgets.QPushButton(self.centralwidget)
        self.btn_start.setEnabled(False)
        self.btn_start.setMinimumSize(QtCore.QSize(0, 46))
        self.btn_start.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.btn_start.setObjectName("btn_start")
        self.verticalLayout_2.addWidget(self.btn_start)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 523, 23))
        self.menuBar.setObjectName("menuBar")
        self.menu = QtWidgets.QMenu(self.menuBar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menuBar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menuBar)
        self.action_connect = QtWidgets.QAction(MainWindow)
        self.action_connect.setObjectName("action_connect")
        self.action1 = QtWidgets.QAction(MainWindow)
        self.action1.setEnabled(False)
        self.action1.setObjectName("action1")
        self.action_save_dir = QtWidgets.QAction(MainWindow)
        self.action_save_dir.setObjectName("action_save_dir")
        self.menu.addAction(self.action_connect)
        self.menu_2.addAction(self.action_save_dir)
        self.menuBar.addAction(self.menu_2.menuAction())
        self.menuBar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "自动曝光"))
        self.tl_progress.setText(_translate("MainWindow", "0/0"))
        self.groupBox.setTitle(_translate("MainWindow", "拍摄参数"))
        self.label_3.setText(_translate("MainWindow", "B门"))
        self.label.setText(_translate("MainWindow", "单张曝光"))
        self.label_2.setText(_translate("MainWindow", "拍摄数量"))
        self.btn_check_event.setText(_translate("MainWindow", "检查事件"))
        self.btn_start.setText(_translate("MainWindow", "开始拍摄"))
        self.menu.setTitle(_translate("MainWindow", "设备"))
        self.menu_2.setTitle(_translate("MainWindow", "文件"))
        self.action_connect.setText(_translate("MainWindow", "连接设备"))
        self.action1.setText(_translate("MainWindow", "断开设备"))
        self.action_save_dir.setText(_translate("MainWindow", "输出目录"))
