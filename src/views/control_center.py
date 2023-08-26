'''

'''
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from Tabify.src.models.transcriber import Transcriber
from Tabify.src.models.transcriber_configs import TranscriberConfigs
from Tabify.src.models.tab import Tab

class ControlCenter(QWidget):
    '''
    
    '''
    transcribed = pyqtSignal(Tab)
    def __init__(self, input_file = None, configs = TranscriberConfigs(), parent = None):
        super(ControlCenter, self).__init__(parent)
        self.input_file = input_file
        self.transcriber = Transcriber(configs)
        self.setupInterface()
    
    def setupInterface(self):
        # todo: set up file selector, slider for weights, number inputs for frets/strings, and
        # either a series of dropdowns or some radio buttons/checkboxes for tunings.
        # we'll have to figure out how to arrange them pleasantly.
        pass

    # todo: this is a slot for a buttonClicked signal
    def executeTranscriber(self):
        tab = self.transcriber.transcribe(self.input_file)
        self.transcribed.emit(tab)