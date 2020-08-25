import sys, logging
from stack import Config, ServerConfig, ServerRunner, ServerRunnerEnvironment, stop_runner

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QTextEdit, QStackedWidget, QSpacerItem,
                               QVBoxLayout, QWidget, QMainWindow, QHBoxLayout, QSizePolicy)
from PySide2.QtCore import Slot, Qt, Signal, QTimer, SIGNAL
from PySide2.QtGui import QFont

from plugins import flask, npm

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
    clicked = Signal()

    def __init__(self, name: str, conf: ServerConfig):
        super(ServerControlWidget, self).__init__()

        self.conf = conf

        self.layout = QHBoxLayout()
        self.label = ClickableLabel(name)
        self.label.clicked.connect(lambda: self.clicked.emit())

        self.btn_start = QPushButton('>')
        self.btn_start.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.btn_start.setEnabled(True)
        self.btn_stop = QPushButton('[ ]')
        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(lambda: self.run_server(name))
        self.btn_stop.clicked.connect(self.stop_server)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.btn_stop)
        self.layout.addWidget(QLabel('*'))

        self.textOutput = QTextEdit(name)
        self.textOutput.setStyleSheet('color: white; background: black; font-family: %s; font-size:11px' % ('Courier New, Monospace'))
        self.textOutput.setReadOnly(True)
        self.textOutput.setLineWrapMode(QTextEdit.NoWrap)
        self.textOutput.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_proc_state)

    @Slot()
    def check_proc_state(self):
        if self.runner_inst.is_alive():
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)

            new_lines = self.runner_inst.output[self.last_pulled_output_index:]
            self.last_pulled_output_index += len(new_lines)
            new_output = ''.join(new_lines)
            self.textOutput.setPlainText(self.textOutput.toPlainText() + new_output)
        else:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.timer.stop()

    def run_server(self, name):
        self.runner_inst = ServerRunner(self.conf, server_env, name)
        self.runner_inst.start()
        self.timer.start()

    @Slot()
    def stop_server(self):
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

    def add_server_tab(self, name:str, conf: ServerConfig):
        tab = ServerControlWidget(name, conf)
        index = self.out_stacked.count()
        tab.clicked.connect(lambda: self.out_stacked.setCurrentIndex(index))
        self.out_stacked.addWidget(tab.textOutput)
        self.tab_layout.addWidget(tab)
        self.server_tabs.append(tab)

    def __init__(self):
        QWidget.__init__(self)

        # window setup
        self.setWindowTitle('Local Server Stack')
        self.layout = QHBoxLayout()

        self.tab_layout = QVBoxLayout()
        self.out_stacked = QStackedWidget()
        self.layout.addLayout(self.tab_layout)
        self.layout.addWidget(self.out_stacked)

        # load settings
        self.conf = Config()
        self.conf.load_yaml(Config.get_config_file())

        self.plugins = [flask.FlaskPlugin, npm.NPMPlugin]

        for name, server_conf in self.conf.get_servers().items():
            tab = self.add_server_tab(name, server_conf)

        self.tab_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(self.layout)

    def closeEvent(self, event):
        # stop all running processes before exiting
        for tab in self.server_tabs:
            tab.stop_server()

if __name__ == "__main__":
    # setup logging
    logging.basicConfig(level=logging.DEBUG)
    
    app = QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())