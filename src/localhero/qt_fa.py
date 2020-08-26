from PySide2.QtGui import QFontDatabase, QFont
import logging, os

FA_PLAY = "\uf04b"
FA_STOP = "\uf04d"
FA_CIRCLE = "\uf111"

def load_regular():
    _load_font('fa-regular-400.ttf')

def load_solid():
    _load_font('fa-solid-900.ttf')

def _load_font(f):
    path = os.path.realpath(os.path.dirname(__file__))
    path = os.path.join(path, 'fonts', f)

    if QFontDatabase.addApplicationFont(path) < 0:
        logging.error('Could not load fa fonts.')

def get_font(size = 32) -> QFont:
    font = QFont()
    font.setFamily('Font Awesome 5 Free')
    font.setPixelSize(size)
    return font