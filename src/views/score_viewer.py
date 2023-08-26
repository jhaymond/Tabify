'''

'''
import fitz
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

DEFAULT_PDF_PATH = '/home/josh/Code/Tabify/output_file.pdf'

class ScoreViewer(QWidget):
    '''
    
    '''
    def __init__(self, pdf_path = DEFAULT_PDF_PATH, parent = None):
        super(ScoreViewer, self).__init__(parent)

        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.scroll_area.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        if pdf_path is not None:
            self.load_pdf(pdf_path)
        else:
            self.display_splash()

    def load_pdf(self, pdf_path):
        '''
        
        '''
        doc = fitz.open(pdf_path)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(alpha=False)

            qtimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            qtimg.bits()  # enforce a copy of the data

            label = QLabel()
            label.setPixmap(QPixmap.fromImage(qtimg))
            label.setAlignment(Qt.AlignHCenter)
            content_layout.addWidget(label)

        content_widget.setLayout(content_layout)
        self.scroll_area.setWidget(content_widget)

    def display_splash(self):
        '''
        
        '''
        # todo: show a blank window with text prompting the user to choose a file in the control
        # center
