import tkinter as tk
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board


class ObjectSelector:
    """
    A class that handles object selection functionality for the board.
    """

    SELECTION_FRAME_PADDING = 2
    SELECTION_FRAME_DASH = (4, 2)
    SELECTION_FRAME_OUTLINE = "black"

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the ObjectSelector.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.toolbox = board.toolbox
        self.selected_objects: List[int] = []
        self.selection_frame_padding: int = ObjectSelector.SELECTION_FRAME_PADDING
        self.selection_frame: Optional[int] = None
        self.selection_start_x: float = 0
        self.selection_start_y: float = 0
        self.is_dragging: bool = False

    def handle_select_tool_click(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the click event when the select tool is active.

        :param event: The mouse event.
        """
        clicked_object = self.canvas.find_withtag(tk.CURRENT)
        if clicked_object:
            if self.selection_frame and self.is_click_inside_selection_frame(event):
                return
            self.select_object(clicked_object[0])
        else:
            if self.is_click_inside_selection_frame(event):
                return
            self.deselect_current_objects()
            self.selection_start_x = self.canvas.canvasx(event.x)
            self.selection_start_y = self.canvas.canvasy(event.y)
            self.selection_frame = self.canvas.create_rectangle(self.selection_start_x, self.selection_start_y,
                                                                self.selection_start_x, self.selection_start_y,
                                                                dash=ObjectSelector.SELECTION_FRAME_DASH,
                                                                outline=ObjectSelector.SELECTION_FRAME_OUTLINE,
                                                                tags="selection_frame")
            self.is_dragging = True

    def handle_select_tool_drag(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the drag event when the select tool is active.

        :param event: The mouse event.
        """
        if self.is_dragging and self.selection_frame:
            current_x: float = self.canvas.canvasx(event.x)
            current_y: float = self.canvas.canvasy(event.y)
            self.canvas.coords(self.selection_frame, self.selection_start_x, self.selection_start_y,
                               current_x, current_y)

    def handle_select_tool_release(self, _: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the release event when the select tool is active.

        :param _: The mouse event (unused).
        """
        if self.is_dragging and self.selection_frame:
            x1, y1, x2, y2 = self.canvas.coords(self.selection_frame)
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            selected_objects = self.canvas.find_enclosed(x1, y1, x2, y2)
            if selected_objects:
                self.select_multiple_objects(list(selected_objects))
            else:
                self.deselect_current_objects()
            self.selection_start_x = 0
            self.selection_start_y = 0
            self.is_dragging = False

    def select_object(self, obj: int) -> None:
        """
        Select a single object.

        :param obj: The ID of the object to select.
        """
        if obj not in self.selected_objects:
            self.deselect_current_objects()
            self.selected_objects = [obj]
            self.draw_selection_frame()
        else:
            self.deselect_current_objects()

    def select_multiple_objects(self, objects: List[int]) -> None:
        """
        Select multiple objects.

        :param objects: The list of object IDs to select.
        """
        self.selected_objects = objects
        self.draw_selection_frame()

    def deselect_current_objects(self) -> None:
        """
        Deselect the currently selected objects.
        """
        self.selected_objects = []
        self.canvas.delete("selection_frame")
        self.selection_frame = None

    def draw_selection_frame(self) -> None:
        """
        Draw the selection frame around the selected objects.
        """
        self.canvas.delete("selection_frame")
        if self.selected_objects:
            bbox = self.canvas.bbox(*self.selected_objects)
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                x1 -= self.selection_frame_padding
                y1 -= self.selection_frame_padding
                x2 += self.selection_frame_padding
                y2 += self.selection_frame_padding
                self.selection_frame = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                                    outline=ObjectSelector.SELECTION_FRAME_OUTLINE,
                                                                    dash=ObjectSelector.SELECTION_FRAME_DASH,
                                                                    tags="selection_frame")

    def is_click_inside_selection_frame(self, event: 'tk.Event[tk.Misc]') -> bool:
        """
        Check if the click event is inside the selection frame.

        :param event: The mouse event.
        :return: True if the click is inside the selection frame, False otherwise.
        """
        if self.selection_frame:
            x = self.canvas.canvasx(event.x)  # type: float
            y = self.canvas.canvasy(event.y)  # type: float
            coords = self.canvas.coords(self.selection_frame)
            x1 = coords[0]
            y1 = coords[1]
            x2 = coords[2]
            y2 = coords[3]
            return x1 <= x <= x2 and y1 <= y <= y2
        return False
