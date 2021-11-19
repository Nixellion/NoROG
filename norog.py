

# from typing import KeysView
from debug import get_logger
log = get_logger("default")

from time import sleep
import pywinusb.hid as hid

import yaml
import time

import profiles
import threading

from PySide2 import QtWidgets, QtGui, QtCore

from configuration import main_config, cache_file

import macro_actions

config = main_config
SHOW_KEY_CODES = config['SHOW_KEY_CODES']
# region UI

import sys, os

from PySide2.QtGui import QIcon#, QFontDatabase, QFont
# from PySide2.QtCore import QFile, QTextStream, QTranslator, QLocale
from PySide2.QtWidgets import QApplication

from paths import  APP_DIR

import os
import sys

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from paths import APP_DIR
from functools import partial



class StrSignal(QtCore.QObject):
    sig = QtCore.Signal(str)

class BroToolTipWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BroToolTipWidget, self).__init__(parent)
        
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.text = QtWidgets.QLabel("Im a tooltip")
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignCenter)

        self.image = QtWidgets.QLabel("")

        # self.mainLayout.addWidget(self.image)
        self.mainLayout.addWidget(self.text)
        # self.setWindowFlags(Qt.ToolTip | Qt.TransparentMode)
        self.setWindowFlags(QtCore.Qt.ToolTip)

        self.setStyleSheet("""
QLabel {
    font-size: 16px;
    color: #fff;
    text-align: center;
}
""")

        # self.effect = QGraphicsDropShadowEffect()
        # self.effect.setBlurRadius(5)
        # self.setGraphicsEffect(self.effect)

        self.movieFormats = [
            ".gif"
        ]


        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(os.path.join(APP_DIR, "background.png")))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def paintEvent(self, event):
        global toast
        print (toast.frameGeometry())
        painter = QPainter()
        painter.drawImage(toast.frameGeometry(), QImage(os.path.join(APP_DIR, "background.png")))


    def setMedia(self, mediaPath):
        name, ext = os.path.splitext(mediaPath)
        if ext in self.movieFormats:
            self.media = QtGui.QMovie(mediaPath)
            self.image.setMovie(self.media)
            self.media.start()
        else:
            self.media = QtGui.QPixmap(mediaPath)
            self.image.setPixmap(self.media)
        self.image.show()

    setImage = setMedia
    setMovie = setMedia

    def setText(self, text):
        self.text.setText(text)
        self.text.show()

    def appendText(self, text):
        self.text.setText(self.text.text() + text)
        self.text.show()

    def empty(self):
        self.text.setText("")
        self.image.setText("")
        self.image.hide()
        self.text.hide()
        self.hide()
        try:
            self.media.deleteLater()
        except Exception as e:
            log.debug(e)
        # TODO Destroy existing objects


class BroToolsTipIssue(QMainWindow):
    def __init__(self):
        super(BroToolsTipIssue, self).__init__()

        self._widget = BroToolTipWidget()
        self.setCentralWidget(self._widget)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(200, 200)
        self.setWindowTitle("NOROG POPUP")

        self.fadeIn = QPropertyAnimation(self, b"windowOpacity")
        self.fadeIn.setDuration(150)
        self.fadeIn.setStartValue(0.0)
        self.fadeIn.setEndValue(1.0)

        self.fadeOut = QPropertyAnimation(self, b"windowOpacity")
        self.fadeOut.setDuration(150)
        self.fadeOut.setStartValue(1.0)
        self.fadeOut.setEndValue(0.0)
        self.fadeOut.finished.connect(self.hide)
        self.isStarted = False

    def setText(self, *args, **kwargs):
        self._widget.setText(*args, **kwargs)

    def resizeEvent(self, event):
        pixmap = QPixmap(os.path.join(APP_DIR, "background.png"))
        region = QRegion(pixmap.mask())
        self.setMask(pixmap.mask())

    def showEvent(self, event):
        self.fadeIn.start()
    
    def hide(self):
        if not self.isStarted:
            print ("START FADEOUT")
            self.fadeOut.start()
            self.isStarted = True

            
        else:   
            self.isStarted = False
            super().hide()

    # def hideEvent(self, event):
    #     print ("HIDING", self.isStarted)
    #     if not self.isStarted:
    #         print ("START FADEOUT")
    #         self.fadeOut.start()
    #         self.isStarted = True
    #         event.ignore()
    #     else:   
    #         self.isStarted = False
    #         QWidget.closeEvent(self, event)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.loadedFile = None
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.clipboard = QClipboard()

        self.appIcon = QIcon(os.path.join(APP_DIR, 'icon.png'))
        self.setWindowIcon(self.appIcon)

        self.mainLayout = QVBoxLayout()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)


        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle("Stuff")

        #self.setStyleSheet(qss)

        self.captureThread = CaptureThread(self)
        self.captureThread.signal_event.sig.connect(partial(self.showToast))
        self.captureThread.start()

        self.timer = None

        self.resize(600, 600)

    def buttonClicked(self, number):
        print (f"Button {number} clicked")

    def showToast(self, text):
        global toast
        # toast = QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), text, self, QtCore.QRect(0, 0, 100, 100), 3000)
        if self.timer:
            self.timer.stop()
            
        toast.setText(text)

        toast.show()
        # pos = QtGui.QCursor.pos()

        screen = QApplication.primaryScreen()
        size = screen.size()
        tgeo = toast.frameGeometry()
        target_pos = [size.width() / 2 - 100, size.height() * 0.6]
        log.debug(f"Tooltip data: {size} {tgeo} {target_pos}")
        toast.move(*target_pos)
        
        if not self.timer:
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.hideToast)
            self.timer.start(2000)
        else:
            self.timer.start(2000)

    def hideToast(self):
        log.debug("Hide toast...")

        # TODO Actions here should be more dynamically handled. This whole thing needs to be refactored to support 2 distinct actions - choose action on press, apply it on toast closed. Show errors in some other way.
        # TODO Handle errors display in some way here
        if profiles.PROFILE_DIRTY:
            profiles.apply_current_profile()
            self.trayIcon.profileStatus.setText(str(main_config['power_presets'][cache_file.get("CURRENT_PROFILE")]['name']))

        if profiles.REFRESH_RATE_DIRTY:
            profiles.apply_main_display_rate()
            self.trayIcon.refreshRateStatus.setText(str(cache_file.get("CURRENT_REFRESH_RATE")))

        toast.hide()
        self.timer.stop()

    def closeEvent(self, event):
        # do stuff
        self.hide()
        event.ignore()


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None, rsg_window=None, app=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        #self.updateAction = menu.addAction("---")
        menu.addSeparator()

        self.profileStatus = menu.addAction(str(main_config['power_presets'][cache_file.get("CURRENT_PROFILE")]['name']))
        self.refreshRateStatus = menu.addAction(str(cache_file.get("CURRENT_REFRESH_RATE")))
        self.profileStatus.setEnabled(False)
        self.refreshRateStatus.setEnabled(False)

        self.exitAction = menu.addAction("Exit")
        self.exitAction.triggered.connect(self.exitApp)
        self.setContextMenu(menu)
        self.parent = parent
        self.app = app

        self.activated.connect(self.activate)

        self.rsg_window = rsg_window


    def activate(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.parent.show()

    def exitApp(self):
        log.info("Closing app...")
        self.app.quit()
        sys.exit()


class CaptureThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.signal_event = StrSignal()
        self.parent = parent

    def run(self):
        # Find devices
        all_devices = hid.find_all_hid_devices()

        kbs = []

        for device in all_devices:
            print (str(device))
            # if "ASUSTek Computer Inc" in str(device):
            kbs.append(device)

        print ("-"*80)
        print (f"Found devices: {str(kbs)}")

        try:
            for device in kbs:
                device.open()

                #set custom raw data handler
                device.set_raw_data_handler(self.sample_handler)

            log.info("Waiting for data...")
            while True:
                sleep(0.5)
            # while not kbhit() and device.is_plugged():
            #     #just keep the device opened to receive events
            #     sleep(0.5)
        finally:
            for device in kbs:
                device.close()
        

    def sample_handler(self, data):
        print_line = False
        if SHOW_KEY_CODES:
            log.info(f"raw: {data}")
            print_line = True
        macros = config['macros']
        key = str(data)
        if key in macros:
            macro_data = macros[key]
            macro_function = getattr(macro_actions, macro_data['action'])
            macro_info = yaml.load(macro_function.__doc__)
            log.info(f"ACTION: {macro_info['name']}")

            macro_tooltip_show = macro_data.get("tooltip_result")

            if macro_tooltip_show:
                self.signal_event.sig.emit(macro_info['name']+":\n...")

            macro_args = macro_data.get("args", [])
            macro_kwargs = macro_data.get("kwargs", {})
            
            result = macro_function(*macro_args, **macro_kwargs)
            if macro_tooltip_show:
                self.signal_event.sig.emit(macro_info['name']+":\n"+str(result))
            print_line = True

        if print_line:
            log.info("-"*80)

# endregion

global toast

def main():
    global toast
    try:
        import ctypes

        myappid = u'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    app = QApplication(sys.argv)

    toast = BroToolsTipIssue()
    mw = MainWindow()
    # mw.show()

    trayIcon = SystemTrayIcon(QIcon(os.path.join(APP_DIR, 'icon.png')), app=app)
    mw.trayIcon = trayIcon
    print ("Show tray icon")
    trayIcon.show()

    sys.exit(app.exec_())



def start_background_thread(func, interval=5, failure_interval=None):
    log.info(f"Starting Thread-{func.__name__}...")
    if not failure_interval:
        failure_interval = interval
    
    def target():
        while True:
            try:
                log.info(f"Running function of Thread-{func.__name__}...")
                func()
                log.info(f"Thread-{func.__name__} sleeping for {interval}...")
                time.sleep(interval)
            except Exception as e:
                log.error(f"Failue in Thread-{func.__name__}: {e} (wait before retrying {failure_interval})", exc_info=True)
                time.sleep(failure_interval)

    t = threading.Thread(target=target)
    t.start()


if __name__ == "__main__":
    start_background_thread(main)
    start_background_thread(profiles.apply_current_profile, interval=600)
