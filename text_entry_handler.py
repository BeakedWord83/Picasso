import tkinter as tk
from typing import Dict, Tuple, Any, TYPE_CHECKING
import pyglet

from fallback_font import FallbackFont

if TYPE_CHECKING:
    from board import Board


class TextEntryHandler:
    """
    A class that handles text entry functionality for the board.
    """

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the TextEntryHandler.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.toolbox = board.toolbox
        self.loaded_fonts: Dict[Tuple[str, int], pyglet.font.Font] = board.loaded_fonts

    def create_text_entry(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Create a new text entry on the board.

        :param event: The event that triggered the text entry creation.
        """
        pyglet_font: Any = self.loaded_fonts.get((self.toolbox.text_font_name, self.toolbox.text_font_size))
        if pyglet_font is None:
            pyglet_font = FallbackFont(self.toolbox.text_font_size)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        text_object_id = self.canvas.create_text(x, y, text="",
                                                 font=(pyglet_font.name, pyglet_font.size),
                                                 fill=self.toolbox.text_color,
                                                 tags=(f"object{len(self.board.objects)}",))
        self.create_text_box(event, text_object_id)

    def create_text_box(self, event: 'tk.Event[tk.Misc]', text_object: int) -> None:
        """
        Create a text box for entering text.

        :param event: The event that triggered the text box creation.
        :param text_object: The ID of the text object on the canvas.
        """
        label = tk.Label(self.canvas, text="Press 'Enter' to confirm\nPress 'Esc' to cancel", )
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        label_window = self.canvas.create_window(canvas_x, canvas_y - 10, window=label, anchor=tk.S)

        text_box = tk.Text(self.canvas, height=1, width=20)
        text_box_window = self.canvas.create_window(canvas_x, canvas_y, window=text_box, anchor=tk.N)
        text_box.insert("1.0", "Enter text here...")
        text_box.focus_set()
        text_box.bind("<FocusIn>", lambda e: text_box.delete("1.0", "end"))
        text_box.bind("<Return>",
                      lambda e: self.update_text_entry(text_box, text_object, label_window, text_box_window))
        text_box.bind("<Escape>",
                      lambda e: self.cancel_text_entry(text_box, text_object, label_window, text_box_window))
        text_box.bind("<FocusOut>",
                      lambda e: self.update_text_entry(text_box, text_object, label_window, text_box_window))

    def cancel_text_entry(self, text_box: tk.Text, text_object: int, label_window: int, text_box_window: int) -> None:
        """
        Cancel the text entry and remove the text object and associated widgets.

        :param text_box: The text box widget.
        :param text_object: The ID of the text object on the canvas.
        :param label_window: The ID of the label window on the canvas.
        :param text_box_window: The ID of the text box window on the canvas.
        """
        self.canvas.delete(text_object)
        self.canvas.delete(label_window)
        self.canvas.delete(text_box_window)
        text_box.destroy()

    def edit_text_entry(self, _: 'tk.Event[tk.Misc]') -> None:
        """
        Edit an existing text entry.

        :param _: The event that triggered the text entry editing (unused).
        """
        if self.board.text_entry is not None:
            self.canvas.itemconfigure(self.board.text_entry, state="hidden")

    def update_text_entry(self, text_box: tk.Text, text_object: int, label_window: int, text_box_window: int) -> None:
        """
        Update the text entry with the entered text and remove the associated widgets.

        :param text_box: The text box widget.
        :param text_object: The ID of the text object on the canvas.
        :param label_window: The ID of the label window on the canvas.
        :param text_box_window: The ID of the text box window on the canvas.
        """
        new_text = text_box.get("1.0", tk.END).strip()
        if new_text:
            # Get the font and size for the text entry
            pyglet_font: Any = self.loaded_fonts.get((self.toolbox.text_font_name, self.toolbox.text_font_size))
            if pyglet_font is None:
                pyglet_font = FallbackFont(self.toolbox.text_font_size)
            # Update the text object with the new text
            self.canvas.itemconfigure(text_object, text=new_text,
                                      font=(pyglet_font.name, pyglet_font.size),
                                      fill=self.toolbox.text_color)
            self.canvas.itemconfigure(text_object, state="normal")
            self.board.objects.append(text_object)
        else:
            self.canvas.delete(text_object)
        self.canvas.delete(label_window)
        self.canvas.delete(text_box_window)
        text_box.destroy()
