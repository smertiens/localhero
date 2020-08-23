import sys
import random
from stack import Config, ServerConfig, ServerRunner, ServerRunnerEnvironment

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton, QTextEdit, QStackedWidget, QSpacerItem,
                               QVBoxLayout, QWidget, QMainWindow, QHBoxLayout, QSizePolicy)
from PySide2.QtCore import Slot, Qt, Signal, QTimer

from plugins import flask, npm

server_env = ServerRunnerEnvironment()

class ServerControlWidget(QWidget):
    
    clicked = Signal(object)
    index = 0
    conf = None
    runner_inst = None
    timer = None

    def __init__(self, name: str, conf: ServerConfig):
        QWidget.__init__(self)

        self.conf = conf
        #self.setStyleSheet('background: white;')

        self.layout = QHBoxLayout()
        self.label = QLabel(name)
        self.btn_start = QPushButton('Start')
        self.btn_start.setEnabled(True)
        self.btn_stop = QPushButton('Stop')
        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(self.run_server)
        self.btn_stop.clicked.connect(self.stop_server)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.btn_stop)
        self.layout.addWidget(QLabel('*'))

        self.textOutput = QTextEdit(name)

        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_proc_state)

    @Slot()
    def check_proc_state(self):
        if self.runner_inst.isAlive():
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)

            self.textOutput.setPlainText(self.runner_inst.output)
        else:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.timer.stop()

    @Slot()
    def run_server(self):
        self.runner_inst = ServerRunner(self.conf, server_env)
        #self.runner_inst.on_output_updated(lambda t: self.textOutput.setPlainText(self.textOutput.toPlainText() + t))
        self.runner_inst.start()
        self.timer.start()

    @Slot()
    def stop_server(self):
        self.runner_inst.stop()

    def emit_clicked(self):
        self.clicked.emit(self)

class MainWindow(QWidget):

    server_tabs = []
    current_tab = 0
    conf = None

    def _hide_all_outputs(self):
        for tab in self.server_tabs:
            tab.textOutput.hide()

    @Slot()
    def tab_clicked(self, tab: ServerControlWidget):
        self._hide_all_outputs()
        tab.textOutput.show()

    def add_server_tab(self, name:str, conf: ServerConfig):
        tab = ServerControlWidget(name, conf)
        tab.clicked.connect(self.tab_clicked)
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
        
        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())