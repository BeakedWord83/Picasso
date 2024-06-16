import tkinter as tk


class WidthDialog(tk.Toplevel):
    """
    A dialog window for changing the width of an object.
    """

    def __init__(self, parent: tk.Misc, initial_value: int) -> None:
        """
        Initialize the WidthDialog.

        :param parent: The parent window.
        :param initial_value: The initial value for the width slider.
        """
        tk.Toplevel.__init__(self, parent)
        self.title("Change Width")
        self.slider = tk.Scale(self, from_=1, to=20, orient=tk.HORIZONTAL)
        self.slider.set(initial_value)  # Set the initial value of the slider
        self.slider.pack()
        self.button = tk.Button(self, text="OK", command=self.ok)
        self.button.pack()
        self.result: float = 0

    def ok(self) -> None:
        """
        Callback function for the OK button.
        Sets the result to the current value of the slider and closes the dialog.
        """
        self.result = self.slider.get()
        self.destroy()
