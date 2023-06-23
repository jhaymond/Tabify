#!/usr/bin/python
'''
Main entrypoint for execution of the application.
'''
import sys
import util
from tabify import Tabify
from PyQt5.QtWidgets import QApplication

def main():
    '''
    Main function of the application. Reads initial arguments and 
    sets up the interface.
    '''
    args = util.read_args(sys.argv[1:])

    app = QApplication(sys.argv)

    window = Tabify(args)

    app.exec()

if __name__ == '__main__':
    main()
