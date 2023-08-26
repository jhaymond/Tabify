'''
Defines the TabEditor class, a specialized text input that is optimized
for letting users edit guitar tablature.
'''
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QLineEdit
from Tabify.src.models.tab import Tab

class TabEditor(QWidget):
    '''
    
    '''
    def __init__(self, tab = None, parent = None):
        super(TabEditor, self).__init__(parent)
        self.tab = tab
        if tab is not None:
            self.setupInterface()
        else:
            self.displaySplash()

    def setupInterface(self):
        # todo: print each line of the tab. there should be some interplay between
        # QLabels and QTextEdits. Maybe this is a separate widget class for each line?
        self.editor = QLineEdit()
        self.editor.setText(str(self.tab))

    def displaySplash(self):
        # todo: show a blank screen with text prompting the user to transcribe a file in the control
        # center
        pass
    
    @pyqtSlot(Tab)
    def changeTab(self, new_tab):
        self.tab = new_tab
        self.editor.setText(str(self.tab))

    def save(self):
        # todo: does the save button need to be its own widget?
        pass
