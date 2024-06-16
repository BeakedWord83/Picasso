import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from typing import TYPE_CHECKING
from file_handler import FileHandler

if TYPE_CHECKING:
    from app import App


class Menu:
    """
    A class representing the main menu of the application.
    """

    LOGO_IMAGE_PATH = "images/logo-color.png"
    LOGO_RESIZE_DIMENSIONS = (200, 200)

    def __init__(self, app: 'App') -> None:
        """
        Initialize the Menu.

        :param app: The application instance.
        """
        self.frame = tk.Frame(app.get_root())
        self.app = app
        self.frame.pack()

        # Load and resize the logo image
        image = Image.open(Menu.LOGO_IMAGE_PATH)
        image = image.resize(Menu.LOGO_RESIZE_DIMENSIONS)
        logo = ImageTk.PhotoImage(image)

        # Create a label with the logo image
        label = tk.Label(self.frame, image=logo)
        self.label_image = logo
        label.pack()

        new_board_button = tk.Button(self.frame, text="New Board", command=self.new_board)
        new_board_button.pack()

        open_board_button = tk.Button(self.frame, text="Open Board", command=self.open_board)
        open_board_button.pack()

    def new_board(self) -> None:
        """
        Create a new board after user confirmation.
        """
        response = messagebox.askquestion("New Board", "Are you sure you want to create a new board?")
        if response == 'yes':
            self.app.create_board()

    def open_board(self) -> None:
        """
        Open an existing board from a file.
        """
        filename = filedialog.askopenfilename(initialdir=FileHandler.DEFAULT_DIR, defaultextension=".pcso", filetypes=[("Picasso Board", "*.pcso")])
        if filename:
            self.app.load_board(filename)

    def show(self) -> None:
        """
        Show the menu frame.
        """
        self.frame.pack()

    def hide(self) -> None:
        """
        Hide the menu frame.
        """
        self.frame.pack_forget()
