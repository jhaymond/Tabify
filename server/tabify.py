'''

'''
import subprocess
from music21.pitch import Pitch
from tab_editor import TabEditor
from score_viewer import ScoreViewer
from guitar import Guitar
from transcriber import Transcriber
from PyQt5.QtWidgets import QMainWindow, QSplitter

class Tabify(QMainWindow):
    '''
    
    '''
    def __init__(self, args, parent = None):
        super(Tabify, self).__init__(parent)

        if 'no_gui' not in args.keys() or not args['no_gui']:
            self.setupInterface(args)
        else:
            self.runCmdline(args)

    def setupInterface(self, args):
        '''
        
        '''
        self.setWindowTitle("Tabify")

        output_path = None
        if 'song_file' in args.keys():
            output_path = '/home/josh/Code/Tabify/output_file.pdf'
            subprocess.run(['mscore3', args['song_file'], '-o', output_path], check=True)

        splitter = QSplitter(self)
        self.scoreViewer = ScoreViewer(output_path, self)
        self.tabEditor = TabEditor(self)


        splitter.addWidget(self.scoreViewer)
        splitter.addWidget(self.tabEditor)

        self.setCentralWidget(splitter)

        self.showMaximized()

    def runCmdline(self, args):
        if 'song_file' in args.keys():
            t = Transcriber(Guitar([
                Pitch('E2'),
                Pitch('A2'),
                Pitch('D3'),
                Pitch('G3'),
                Pitch('B3'),
                Pitch('E4')]))
            
            tab = t.transcribe(args['song_file'])
            print(str(tab))
