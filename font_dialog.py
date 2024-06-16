import tkinter as tk
from typing import Optional


class FontDialog(tk.Toplevel):
    """
    A dialog window for changing the font.
    """

    def __init__(self, parent: tk.Misc, initial_font: str) -> None:
        """
        Initialize the FontDialog.

        :param parent: The parent window.
        :param initial_font: The initial font value.
        """
        super().__init__(parent)
        self.title("Change Font")
        self.result: Optional[str] = None

        self.font_var = tk.StringVar(value=initial_font)
        font_dropdown = tk.OptionMenu(self, self.font_var, "Arial", "Georgia", "Calibri",
                                      "Courier", "Verdana")
        font_dropdown.pack(padx=10, pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        ok_button = tk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def on_ok(self) -> None:
        """
        Callback function for the OK button.
        Sets the result to the selected font and closes the dialog.
        """
        self.result = self.font_var.get()
        self.destroy()

    def on_cancel(self) -> None:
        """
        Callback function for the Cancel button.
        Closes the dialog without setting the result.
        """
        self.destroy()
