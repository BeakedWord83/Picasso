import tkinter as tk
from PIL.ImageTk import PhotoImage


class ButtonItem:
    """
    A class representing a button item with an associated image.
    """
    def __init__(self, button: tk.Button, image: PhotoImage):
        """
        Initialize the ButtonItem.

        :param button: The button widget.
        :param image: The image associated with the button.
        """
        self.button = button
        self.image = image
