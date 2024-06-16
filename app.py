import os
import tkinter as tk
from typing import Dict

from board import Board
from menu import Menu
from toolbox import Toolbox
import json
import pyglet


class App:
    """
    A class representing the main application.
    """
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the App.

        :param root: The root Tk instance.
        """
        root.title("Picasso")
        self.__root = root
        self.loaded_fonts: Dict[tuple[str, int], pyglet.font.Font] = {}
        self.load_fonts()
        self.menu = Menu(self)
        self.show_menu_window()

    def get_root(self) -> tk.Tk:
        """
        Get the root Tk instance.

        :return: The root Tk instance.
        """
        return self.__root

    def show_menu_window(self) -> None:
        """
        Show the menu window.
        """
        self.menu.show()

    def create_board(self) -> None:
        """
        Create a new board.
        """
        self.menu.hide()
        toolbox = Toolbox(self)
        Board(self, toolbox, self.loaded_fonts)

    def load_fonts(self) -> None:
        """
        Load the fonts from the "fonts" directory.
        """
        font_dir = "fonts"
        for font_file in os.listdir(font_dir):
            if font_file.endswith(".ttf"):
                font_name = os.path.splitext(font_file)[0]
                font_path = os.path.join(font_dir, font_file)
                pyglet.font.add_file(font_path)
                for size in range(8, 73, 4):  # Load font sizes from 8 to 72 in steps of 4
                    pyglet_font = pyglet.font.load(font_name, size)
                    self.loaded_fonts[(font_name, size)] = pyglet_font

    def load_board(self, filename: str) -> None:
        """
        Load a board from a file.

        :param filename: The name of the file to load the board from.
        """
        with open(filename, 'r') as f:
            board_state = json.load(f)
        self.menu.hide()
        toolbox = Toolbox(self)
        board = Board(self, toolbox, self.loaded_fonts)
        board.file_handler.load_objects(board_state['objects'])
