'''

'''
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from Tabify.src.views.control_center import ControlCenter
from Tabify.src.views.score_viewer import ScoreViewer, DEFAULT_PDF_PATH
from Tabify.src.views.tab_editor import TabEditor
from Tabify.src.models.transcriber import Transcriber
from Tabify.src.models.transcriber_configs import TranscriberConfigs

class Tabify:
    '''
    
    '''
    def __init__(self, argv):
        self.settings = self.read_args(argv)

    def read_args(self, args):
        '''
        
        '''
        arg_dict = {}
        i = 0

        while i < len(args):
            if args[i] == '--no-gui':
                arg_dict['no_gui'] = True
            elif args[i] in ('-f', '--file'):
                arg_dict['input_file'] = args[i + 1]
                i += 1
            elif args[i] in ('-o', '--output-file'):
                arg_dict['output_file'] = args[i + 1]
                i += 1
            i += 1

        return arg_dict

    def run(self):
        if 'help' in self.settings:
            self.usage_screen()
            return

        if 'no_gui' not in self.settings or not self.settings['no_gui']:
            self.run_gui()
        else:
            self.run_cmdline()

    def run_gui(self):
        '''
        
        '''
        input_file = None
        configs = self.get_transcriber_configs()
        if 'input_file' in self.settings:
            input_file = self.settings['input_file']
            subprocess.run(['mscore3', input_file, '-o', DEFAULT_PDF_PATH], check=True)

        app = QApplication()

        window = QMainWindow()
        window.setWindowTitle("Tabify")

        tab_editor = TabEditor(parent = window)
        score_viewer = ScoreViewer(parent = window)
        # todo: hook up a signal-slot for updating the score viewer

        control_center = ControlCenter(input_file, configs, window)
        control_center.transcribed.connect(tab_editor.changeTab)
        if input_file is not None:
            control_center.executeTranscriber()

        vbox = QVBoxLayout(window)
        vbox.addWidget(control_center)
        vbox.addWidget(score_viewer)
        vbox.addWidget(tab_editor)
        window.setLayout(vbox)

        window.show()
        app.exec()

    def run_cmdline(self):
        if 'input_file' in self.settings:
            transcriber = Transcriber(self.get_transcriber_configs())

            tab = transcriber.transcribe(self.settings['input_file'])
            if 'output_file' in self.settings:
                pass # todo: stick str(tab) in the file
            else:
                print(str(tab))
        else:
            self.usage_screen()

    def get_transcriber_configs(self):
        # todo: look for relevant settings in the settings dictionary and pass them into the
        # constructor
        return TranscriberConfigs()

    def usage_screen(self):
        pass
