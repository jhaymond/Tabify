#!/usr/bin/python
'''
Main entrypoint for execution of the application.
'''
import sys
from Tabify.src.models.tabify import Tabify

def main():
    '''
    Main function of the application. Initializes the QApplication.
    '''
    tabify = Tabify(sys.argv)
    tabify.run()

if __name__ == '__main__':
    main()
