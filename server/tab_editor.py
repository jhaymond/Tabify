'''
Defines the TabEditor class, a specialized text input that is optimized
for letting users edit guitar tablature.
'''
from PyQt5.QtWidgets import QWidget

class TabEditor(QWidget):
    def __init__(self, tab = None, parent = None):
        super(TabEditor, self).__init__(parent)
        self.tab = tab
        if tab is None:
            self.displaySplash()
        else:
            self.setupInterface()
    
    def setupInterface(self):
        # todo: print each line of the tab. there should be some interplay between
        # QLabels and QTextEdits. Maybe this is a separate widget class for each line?
        for f in self.tab.format():
            if f.type == 'fretting':
                pass # todo: initialize a QWidget for a tab fretting
            elif f.type == 'spacing':
                pass # todo: initialize a QWidget for a tab spacer

    def displaySplash(self):
        # todo: display a button that kicks off the transcription process.
        # it should probably know whether the user has selected a song in the 
        # score viewer already. Maybe this means the design needs to be a little different?
        pass
