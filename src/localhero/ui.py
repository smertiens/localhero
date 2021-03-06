import sys, os
import logging
from localhero.core import Config, ServerConfig, ServerRunner, ServerRunnerEnvironment, stop_runner, MissingConfig

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QTextEdit, QStackedWidget, QSpacerItem,
                               QVBoxLayout, QWidget, QMainWindow, QHBoxLayout, QSizePolicy)
from PySide2.QtCore import Slot, Qt, Signal, QTimer, SIGNAL, QMargins
from PySide2.QtGui import QTextCursor

from localhero.plugins import flask, node
import localhero.qt_fa as qt_fa
from localhero import fonts, style

server_env = ServerRunnerEnvironment()


class ClickableLabel(QLabel):

    clicked = Signal()

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()


class ServerControlWidget(QWidget):

    index = 0
    conf = None
    runner_inst = None
    timer = None
    last_pulled_output_index = 0
    clicked = Signal(object)
    selected = False

    def __init__(self, name: str, conf: ServerConfig):
        super().__init__()

        self.conf = conf

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout = QHBoxLayout()
        self.label = ClickableLabel(name)
        self.label.clicked.connect(lambda: self.clicked.emit(self))

        self.btn_start = QPushButton(qt_fa.FA_PLAY)
        self.btn_start.setFlat(True)
        self.btn_start.setFont(qt_fa.get_font(20))

        self.btn_start.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.btn_start.setEnabled(True)

        self.btn_stop = QPushButton(qt_fa.FA_STOP)
        self.btn_stop.setFlat(True)
        self.btn_stop.setFont(qt_fa.get_font(20))
        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(lambda: self.run_server(name))
        self.btn_stop.clicked.connect(self.stop_server)

        self.status_indic = QLabel(qt_fa.FA_CIRCLE)
        self.status_indic.setProperty('class', 'indicator_off')
        self.status_indic.setFont(qt_fa.get_font(20))

        self.layout.addWidget(self.status_indic)
        self.layout.addWidget(self.label)
        self.layout.addSpacerItem(QSpacerItem(20,20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.btn_stop)

        self.textOutput = QTextEdit()
        self.textOutput.setReadOnly(True)
        self.textOutput.setLineWrapMode(QTextEdit.NoWrap)
        self.textOutput.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_proc_state)

    def mouseReleaseEvent(self, ev):
        self.emit_clicked()

    def update_state(self):
        self.setStyle(self.style())
        self.label.setStyle(self.label.style())

    def flush_proc_output(self):

        # update process outputs
        # maintain scroll position and selection
        scroll_y = self.textOutput.verticalScrollBar().value()
        scroll_x = self.textOutput.horizontalScrollBar().value()
        sel_start = self.textOutput.textCursor().selectionStart()
        sel_end = self.textOutput.textCursor().selectionEnd()

        new_lines = self.runner_inst.output[self.last_pulled_output_index:]
        self.last_pulled_output_index += len(new_lines)
        new_output = ''.join(new_lines)
        self.textOutput.setPlainText(
            self.textOutput.toPlainText() + new_output)

        cur = self.textOutput.textCursor()
        cur.setPosition(sel_start)
        cur.setPosition(sel_end, QTextCursor.KeepAnchor)
        self.textOutput.setTextCursor(cur)

        self.textOutput.verticalScrollBar().setValue(scroll_y)
        self.textOutput.horizontalScrollBar().setValue(scroll_x)


    @Slot()
    def check_proc_state(self):
        self.flush_proc_output()
            
        if self.runner_inst.is_alive():
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.status_indic.setProperty('class', 'indicator_on')
            self.status_indic.setStyle(self.status_indic.style())
            
        else:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.status_indic.setProperty('class', 'indicator_off')
            self.status_indic.setStyle(self.status_indic.style())
            
            self.timer.stop()

    def run_server(self, name):
        self.runner_inst = ServerRunner(self.conf, server_env, name)
        self.runner_inst.start()
        self.timer.start()

    @Slot()
    def stop_server(self):
        if self.runner_inst is not None:
            stop_runner(self.runner_inst)

    def emit_clicked(self):
        self.clicked.emit(self)


class MainWindow(QWidget):

    server_tabs = []
    current_tab = 0
    conf = None

    def _hide_all_outputs(self):
        for tab in self.server_tabs:
            tab.textOutput.hide()

    def server_tab_clicked(self, index, t):
        self.out_stacked.setCurrentIndex(index)

        for tab in self.server_tabs:
            if tab == t:
                tab.selected = True
                tab.setProperty('selected', True)
            else:
                tab.selected = False
                tab.setProperty('selected', False)

            tab.update_state()
            
    def add_server_tab(self, name: str, conf: ServerConfig):
        tab = ServerControlWidget(name, conf)
        index = self.out_stacked.count()

        tab.clicked.connect(lambda t: self.server_tab_clicked(index, t))

        self.out_stacked.addWidget(tab.textOutput)
        self.tab_layout.addWidget(tab)
        self.server_tabs.append(tab)

    def __init__(self):
        QWidget.__init__(self)

        # window setup
        self.setWindowTitle(QApplication.applicationName())
        self.layout = QHBoxLayout()

        self.tab_layout = QVBoxLayout()
        self.out_stacked = QStackedWidget()
        self.layout.addLayout(self.tab_layout)
        self.layout.addWidget(self.out_stacked)
        self.layout.setStretchFactor(self.out_stacked, 2)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # load settings
        self.conf = Config()
        self.conf.load_yaml(self.conf.get_config_file())
        
        for name, server_conf in self.conf.get_servers().items():
            self.add_server_tab(name, server_conf)

        # select first tab 
        self.server_tab_clicked(0, self.server_tabs[0])

        self.tab_layout.addSpacerItem(QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.info_label = QLabel(QApplication.applicationName() + ' ' + QApplication.applicationVersion())
        self.info_label.setObjectName('info-label')
        self.tab_layout.addWidget(self.info_label)

    def closeEvent(self, event):
        # stop all running processes before exiting
        for tab in self.server_tabs:
            tab.stop_server()

def main():
    # setup logging
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    app.setApplicationName('Localhero')
    app.setApplicationVersion('0.1.0')

    styles = os.path.realpath(os.path.join(os.path.dirname(style.__file__), 'app.css'))

    with open(styles, 'r') as f:
        app.setStyleSheet(f.read())

    qt_fa.load_solid()

    widget = MainWindow()
    widget.setObjectName('main-window')
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
