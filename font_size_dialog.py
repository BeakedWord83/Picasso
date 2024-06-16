import tkinter as tk
from typing import Optional


class FontSizeDialog(tk.Toplevel):
    """
    A dialog window for changing the font size.
    """

    def __init__(self, parent: tk.Misc, initial_size: str) -> None:
        """
        Initialize the FontSizeDialog.

        :param parent: The parent window.
        :param initial_size: The initial font size value.
        """
        super().__init__(parent)
        self.title("Change Font Size")
        self.result: Optional[str] = None

        self.size_var = tk.StringVar(value=initial_size)
        size_dropdown = tk.OptionMenu(self, self.size_var, "8", "10", "12", "14", "16", "18", "20", "24", "28", "32")
        size_dropdown.pack(padx=10, pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        ok_button = tk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def on_ok(self) -> None:
        """
        Callback function for the OK button.
        Sets the result to the selected font size and closes the dialog.
        """
        self.result = self.size_var.get()
        self.destroy()

    def on_cancel(self) -> None:
        """
        Callback function for the Cancel button.
        Closes the dialog without setting the result.
        """
        self.destroy()
