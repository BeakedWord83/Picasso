import tkinter as tk
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board


class ObjectMover:
    """
    A class that handles object movement functionality for the board.
    """

    NORMALIZED_VELOCITY = 2
    SCROLL_VELOCITY_MULTIPLIER = 0.5
    SCROLL_VELOCITY_DECAY = 0.9
    SMOOTH_SCROLL_DELAY = 20

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the ObjectMover.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.toolbox = board.toolbox
        self.object_selector = board.object_selector
        self.scroll_velocity_x: float = 0
        self.scroll_velocity_y: float = 0
        self.is_scrolling: bool = False
        self.is_moving: bool = False
        self.drag_start_x: Optional[int] = None
        self.drag_start_y: Optional[int] = None

    def start_move(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Start moving the selected objects.

        :param event: The mouse event.
        """
        if self.object_selector.selected_objects:
            self.canvas.tag_raise("selection_frame")
            self.is_moving = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def continue_move(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Continue moving the selected objects.

        :param event: The mouse event.
        """
        if self.is_moving and self.drag_start_x is not None and self.drag_start_y is not None:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            for obj in self.object_selector.selected_objects:
                self.canvas.move(obj, dx, dy)
            self.canvas.move("selection_frame", dx, dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def end_move(self) -> None:
        """
        End the object movement.
        """
        self.is_moving = False
        self.drag_start_x = None
        self.drag_start_y = None

    def perform_move(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Perform the movement of the selected objects.

        :param event: The mouse event.
        """
        if self.object_selector.selected_objects:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            dx = x - self.board.last_x
            dy = y - self.board.last_y
            for obj in self.object_selector.selected_objects:
                self.canvas.move(obj, dx, dy)
            self.canvas.move("selection_frame", dx, dy)
            self.board.last_x = x
            self.board.last_y = y

    def move_view(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Move the view (scroll) based on the mouse movement.

        :param event: The mouse event.
        """
        dx = event.x - self.board.last_x
        dy = event.y - self.board.last_y

        # Normalize the velocity to a fixed value
        dx = -ObjectMover.NORMALIZED_VELOCITY if dx > 0 else ObjectMover.NORMALIZED_VELOCITY if dx < 0 else 0
        dy = -ObjectMover.NORMALIZED_VELOCITY if dy > 0 else ObjectMover.NORMALIZED_VELOCITY if dy < 0 else 0

        self.scroll_velocity_x = dx * ObjectMover.SCROLL_VELOCITY_MULTIPLIER
        self.scroll_velocity_y = dy * ObjectMover.SCROLL_VELOCITY_MULTIPLIER

        self.board.last_x = event.x
        self.board.last_y = event.y

        self.ensure_smooth_scroll()

    def smooth_scroll(self) -> None:
        """
        Perform smooth scrolling based on the scroll velocity.
        """
        if abs(self.scroll_velocity_x) >= 0.01 or abs(self.scroll_velocity_y) >= 0.01:
            self.canvas.xview_scroll(int(self.scroll_velocity_x), "units")
            self.canvas.yview_scroll(int(self.scroll_velocity_y), "units")

            self.scroll_velocity_x *= 0.9
            self.scroll_velocity_y *= 0.9

            self.board.app.get_root().after(20, self.smooth_scroll)
        else:
            self.is_scrolling = False

    def ensure_smooth_scroll(self) -> None:
        """
        Ensure smooth scrolling by starting the scrolling process if not already scrolling.
        """
        if not self.is_scrolling:
            self.is_scrolling = True
            self.smooth_scroll()
