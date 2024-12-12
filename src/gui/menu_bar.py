from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal

class MenuBar(QMenuBar):
    file_opened = pyqtSignal(str)
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_menus()

    def init_menus(self):
        file_menu = QMenu("File", self)
        self.addMenu(file_menu)

        open_file_action = QAction("Open", self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        save_file_action = QAction("Save", self)
        file_menu.addAction(save_file_action)
        
        save_as_file_action = QAction("Save As", self)
        file_menu.addAction(save_as_file_action)
        
        exit_action = QAction("Exit", self)
        file_menu.addAction(exit_action)
        
        edit_menu = QMenu("Edit", self)
        self.addMenu(edit_menu)
        
        copy_action = QAction("Copy", self)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        edit_menu.addAction(paste_action)
        
        cut_action = QAction("Cut", self)
        edit_menu.addAction(cut_action)
        
        select_all_action = QAction("Select All", self)
        edit_menu.addAction(select_all_action)
        
        view_menu = QMenu("View", self)
        self.addMenu(view_menu)
        
        zoom_in_action = QAction("Zoom In", self)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Reset Zoom", self)
        view_menu.addAction(reset_zoom_action)
        
        help_menu = QMenu("Help", self)
        self.addMenu(help_menu)
        
        about_action = QAction("About", self)
        help_menu.addAction(about_action)
    
    def open_file(self):
        self.main_window.open_file_dialog()
