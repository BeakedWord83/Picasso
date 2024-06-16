from typing import TYPE_CHECKING
import tkinter as tk
if TYPE_CHECKING:
    from board import Board


class FillHandler:
    """
    A class that handles the fill functionality for the board.
    """

    FILL_TOLERANCE = 5

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the FillHandler.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.toolbox = board.toolbox

    def fill_area(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Fill the area of the clicked object with the selected fill color.

        :param event: The event that triggered the fill action.
        """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_items = self.canvas.find_overlapping(x - FillHandler.FILL_TOLERANCE, y - FillHandler.FILL_TOLERANCE,
                                                     x + FillHandler.FILL_TOLERANCE, y + FillHandler.FILL_TOLERANCE)
        if clicked_items:
            clicked_item = clicked_items[-1]
            item_type = self.canvas.type(clicked_item)  # type: ignore
            if item_type in ["line", "text", "polygon"]:
                self.canvas.itemconfig(clicked_item, fill=self.toolbox.fill_color)
            elif item_type in ["rectangle", "oval"]:
                self.canvas.itemconfig(clicked_item, fill=self.toolbox.fill_color, outline=self.toolbox.fill_color)
