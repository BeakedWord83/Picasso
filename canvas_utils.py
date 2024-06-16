from typing import TYPE_CHECKING
import tkinter as tk

if TYPE_CHECKING:
    from board import Board


class CanvasUtils:
    """
    A class that provides utility functions for the canvas.
    """

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the CanvasUtils.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.toolbox = board.toolbox

    def erase_objects(self, x: float, y: float) -> None:
        """
        Erase objects at the given coordinates using the eraser tool.

        :param x: The x-coordinate of the eraser position.
        :param y: The y-coordinate of the eraser position.
        """
        eraser_size = self.toolbox.eraser_width
        eraser_bbox = (x - eraser_size // 2, y - eraser_size // 2,
                       x + eraser_size // 2, y + eraser_size // 2)
        overlapping_objects = self.canvas.find_overlapping(*eraser_bbox)
        for obj in overlapping_objects:
            if obj in self.canvas.find_all() and "eraser_frame" not in self.canvas.gettags(obj):
                item_type = self.canvas.type(obj)  # type: ignore
                if item_type == "line":
                    coords = self.canvas.coords(obj)
                    new_coords = []
                    i = 0
                    while i < len(coords):
                        px, py = coords[i], coords[i + 1]
                        if not (eraser_bbox[0] <= px <= eraser_bbox[2] and eraser_bbox[1] <= py <= eraser_bbox[3]):
                            new_coords.append(px)
                            new_coords.append(py)
                        else:
                            if len(new_coords) >= 4:
                                new_obj = self.new_object(obj, new_coords)
                                self.board.objects.append(new_obj)
                            new_coords = []
                        i += 2
                    if len(new_coords) >= 4:
                        new_obj = self.new_object(obj, new_coords)
                        self.board.objects.append(new_obj)
                    self.canvas.delete(obj)
                    if obj in self.board.objects:
                        self.board.objects.remove(obj)
                        break
                elif item_type == "rectangle" or item_type == "oval" or item_type == "polygon" or item_type == "text":
                    self.canvas.delete(obj)
                    if obj in self.board.objects:
                        self.board.objects.remove(obj)
                        break

    def new_object(self, obj: int, new_coords: list[float]) -> int:
        """
        Create a new object with the given coordinates and properties.

        :param obj: The original object.
        :param new_coords: The new coordinates for the object.
        :return: The ID of the new object.
        """
        fill = self.canvas.itemcget(obj, "fill")  # type: ignore
        width = self.canvas.itemcget(obj, "width")  # type: ignore
        new_obj = self.canvas.create_line(*new_coords, fill=fill,
                                          width=width,
                                          tags=(f"object{len(self.board.objects)}",),
                                          smooth=True)
        return new_obj

    def move_eraser_frame(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Move the eraser frame based on the mouse movement.

        :param event: The mouse event.
        """
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        eraser_size = self.toolbox.eraser_width
        eraser_bbox = (canvas_x - eraser_size // 2, canvas_y - eraser_size // 2,
                       canvas_x + eraser_size // 2, canvas_y + eraser_size // 2)
        if self.board.eraser_frame is None:
            self.board.eraser_frame = self.canvas.create_rectangle(*eraser_bbox, outline="red", tags="eraser_frame")
        else:
            self.canvas.coords(self.board.eraser_frame, *eraser_bbox)

    def return_to_middle(self) -> None:
        """
        Move the canvas view to the middle of the board.
        """
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)
