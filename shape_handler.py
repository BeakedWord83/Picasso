from typing import List, Tuple, Optional, TYPE_CHECKING
import tkinter as tk

if TYPE_CHECKING:
    from board import Board


class ShapeHandler:
    """
    A class that handles shape drawing functionality for the board.
    """

    POLYGON_POINT_SIZE = 6
    POLYGON_POINT_HOVER_SIZE = 10
    POLYGON_START_POINT_COLOR = "green"
    POLYGON_PREVIEW_LINE_FILL = "gray"
    POLYGON_PREVIEW_LINE_DASH = (4, 4)
    SHAPE_FILL_COLOR = "black"
    SHAPE_WIDTH = 5

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the ShapeHandler.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.toolbox = board.toolbox
        self.current_object_tag: str = ""
        self.current_object: int = 0
        self.pen_points: List[Tuple[float, float]] = []
        self.temp_line: int = 0
        self.temp_shape: int = 0
        self.polygon_points: List[Tuple[float, float]] = []
        self.polygon_temp_shapes: List[int] = []
        self.polygon_preview_line: Optional[int] = None
        self.canvas.bind("<Motion>", self.handle_polygon_hover)

    def start_shape(self) -> None:
        """
        Start drawing a new shape based on the current tool.
        """
        if self.toolbox.current_tool == "Rectangle":
            self.temp_shape = self.canvas.create_rectangle(self.board.last_x, self.board.last_y,
                                                           self.board.last_x, self.board.last_y,
                                                           width=ShapeHandler.SHAPE_WIDTH)
        elif self.toolbox.current_tool == "Circle":
            self.temp_shape = self.canvas.create_oval(self.board.last_x, self.board.last_y,
                                                      self.board.last_x, self.board.last_y,
                                                      width=ShapeHandler.SHAPE_WIDTH)
        elif self.toolbox.current_tool == "Triangle":
            self.temp_shape = self.canvas.create_polygon(self.board.last_x, self.board.last_y,
                                                         self.board.last_x, self.board.last_y,
                                                         self.board.last_x, self.board.last_y,
                                                         width=ShapeHandler.SHAPE_WIDTH)
        elif self.toolbox.current_tool == "Line":
            self.temp_shape = self.canvas.create_line(self.board.last_x, self.board.last_y,
                                                      self.board.last_x, self.board.last_y,
                                                      width=ShapeHandler.SHAPE_WIDTH)
        elif self.toolbox.current_tool == "Polygon":
            self.polygon_points = [(self.board.last_x, self.board.last_y)]

    def update_shape(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Update the current shape based on the mouse movement.

        :param event: The mouse event.
        """
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        if self.toolbox.current_tool == "Rectangle":
            self.canvas.coords(self.temp_shape, self.board.last_x, self.board.last_y, canvas_x, canvas_y)
        elif self.toolbox.current_tool == "Circle":
            x1, y1 = self.board.last_x, self.board.last_y
            x2, y2 = canvas_x, canvas_y
            radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.coords(self.temp_shape, cx - radius, cy - radius, cx + radius, cy + radius)
        elif self.toolbox.current_tool == "Triangle":
            # Calculate the coordinates of the triangle based on the mouse position
            x1, y1 = self.board.last_x, self.board.last_y
            x2, y2 = canvas_x, canvas_y
            dx, dy = x2 - x1, y2 - y1
            side = (dx ** 2 + dy ** 2) ** 0.5
            if side != 0:
                h = side * (3 ** 0.5) / 2
                x3 = x1 + dx / 2
                y3 = y1 + (y2 - y1) / 2 + h * dx / side
                self.canvas.coords(self.temp_shape, x1, y1, x2, y2, x3, y3)
        elif self.toolbox.current_tool == "Line":
            self.canvas.coords(self.temp_shape, self.board.last_x, self.board.last_y, canvas_x, canvas_y)

    def draw_pen(self, x: float, y: float) -> None:
        """
        Draw a pen line based on the mouse movement.

        :param x: The x-coordinate of the mouse.
        :param y: The y-coordinate of the mouse.
        """
        if self.board.drawing and self.toolbox.current_tool == "Pen":
            if not self.current_object_tag:
                self.current_object_tag = f"object{len(self.board.objects)}"
                self.current_object = 0
            self.pen_points.append((x, y))
            if len(self.pen_points) >= 2:
                if self.temp_line is not None:
                    self.canvas.delete(self.temp_line)
                self.temp_line = self.canvas.create_line(*self.pen_points, fill=self.toolbox.pen_color,
                                                         width=self.toolbox.pen_width, tags=self.current_object_tag)
            else:
                self.temp_line = self.canvas.create_line(*(self.pen_points[0] * 2), fill=self.toolbox.pen_color,
                                                         width=self.toolbox.pen_width, tags=self.current_object_tag)
        self.current_object = self.temp_line
        self.board.last_x = x
        self.board.last_y = y

    def finalize_shape(self) -> None:
        """
        Finalize the current shape and add it to the board objects.
        """
        if not self.current_object_tag:
            self.current_object_tag = f"object{len(self.board.objects)}"
            self.current_object = 0
        shape: Optional[int] = None
        if self.toolbox.current_tool == "Rectangle":
            coords = self.canvas.coords(self.temp_shape)
            shape = self.canvas.create_rectangle(*coords, fill=ShapeHandler.SHAPE_FILL_COLOR, width=self.toolbox.pen_width)
            self.canvas.delete(self.temp_shape)
        elif self.toolbox.current_tool == "Circle":
            coords = self.canvas.coords(self.temp_shape)
            shape = self.canvas.create_oval(*coords, fill=ShapeHandler.SHAPE_FILL_COLOR, width=self.toolbox.pen_width)
            self.canvas.delete(self.temp_shape)
        elif self.toolbox.current_tool == "Triangle":
            coords = self.canvas.coords(self.temp_shape)
            shape = self.canvas.create_polygon(*coords, fill=ShapeHandler.SHAPE_FILL_COLOR, width=self.toolbox.pen_width)
            self.canvas.delete(self.temp_shape)
        elif self.toolbox.current_tool == "Line":
            coords = self.canvas.coords(self.temp_shape)
            shape = self.canvas.create_line(*coords, fill=ShapeHandler.SHAPE_FILL_COLOR, width=self.toolbox.pen_width)
            self.canvas.delete(self.temp_shape)
        if shape is not None:
            self.canvas.itemconfig(shape, tags=self.current_object_tag)
            self.current_object = shape

    def draw_polygon_point(self, x: float, y: float) -> None:
        """
        Draw a polygon point on the canvas.

        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.
        """
        is_starting_point = len(self.polygon_points) == 0
        point_color = ShapeHandler.POLYGON_START_POINT_COLOR if is_starting_point else "white"

        point = self.canvas.create_oval(x - ShapeHandler.POLYGON_POINT_SIZE, y - ShapeHandler.POLYGON_POINT_SIZE,
                                        x + ShapeHandler.POLYGON_POINT_SIZE, y + ShapeHandler.POLYGON_POINT_SIZE,
                                        fill=point_color, outline="black", width=2,
                                        tags=("polygon_point",))

        self.polygon_points.append((x, y))  # Append the point to the polygon_points list
        self.polygon_temp_shapes.append(point)
        self.update_polygon_preview()

    def update_polygon_preview(self) -> None:
        """
        Update the preview of the polygon shape.
        """
        if len(self.polygon_points) > 1:
            if self.polygon_preview_line is not None:
                self.canvas.delete(self.polygon_preview_line)
            points = self.polygon_points + [self.polygon_points[0]]
            self.polygon_preview_line = self.canvas.create_line(points, fill=ShapeHandler.POLYGON_PREVIEW_LINE_FILL,
                                                                dash=ShapeHandler.POLYGON_PREVIEW_LINE_DASH)

    def handle_polygon_hover(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the hover effect on polygon points.

        :param event: The mouse event.
        """
        if self.toolbox.current_tool == "Polygon":
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            for point in self.polygon_temp_shapes:
                coords = self.canvas.coords(point)
                x, y = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
                distance = ((canvas_x - x) ** 2 + (canvas_y - y) ** 2) ** 0.5
                if distance <= ShapeHandler.POLYGON_POINT_SIZE:
                    self.canvas.coords(point,
                                       x - ShapeHandler.POLYGON_POINT_HOVER_SIZE,
                                       y - ShapeHandler.POLYGON_POINT_HOVER_SIZE,
                                       x + ShapeHandler.POLYGON_POINT_HOVER_SIZE,
                                       y + ShapeHandler.POLYGON_POINT_HOVER_SIZE)
                else:
                    self.canvas.coords(point,
                                       x - ShapeHandler.POLYGON_POINT_SIZE, y - ShapeHandler.POLYGON_POINT_SIZE,
                                       x + ShapeHandler.POLYGON_POINT_SIZE, y + ShapeHandler.POLYGON_POINT_SIZE)

    def finalize_polygon(self) -> None:
        """
        Finalize the polygon shape and add it to the board objects.
        """
        if len(self.polygon_points) >= 3:
            if not self.current_object_tag:
                self.current_object_tag = f"object{len(self.board.objects)}"
                self.current_object = 0
            shape = self.canvas.create_polygon(self.polygon_points, fill="black",
                                               width=self.toolbox.pen_width, tags=self.current_object_tag)
            self.current_object = shape
        self.clear_polygon_points()

    def handle_polygon_click(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the click event for polygon drawing.

        :param event: The mouse event.
        """
        if self.toolbox.current_tool == "Polygon":
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            if len(self.polygon_points) > 0:
                start_x, start_y = self.polygon_points[0]
                if abs(canvas_x - start_x) <= ShapeHandler.POLYGON_POINT_HOVER_SIZE and abs(
                        canvas_y - start_y) <= ShapeHandler.POLYGON_POINT_HOVER_SIZE:
                    self.finalize_polygon()
                    return

                for point_x, point_y in self.polygon_points[1:]:
                    if abs(canvas_x - point_x) <= ShapeHandler.POLYGON_POINT_HOVER_SIZE and abs(
                            canvas_y - point_y) <= ShapeHandler.POLYGON_POINT_HOVER_SIZE:
                        return
            self.draw_polygon_point(canvas_x, canvas_y)

    def clear_polygon_points(self) -> None:
        """
        Clear the polygon points and temporary shapes.
        """
        self.polygon_points = []
        for shape in self.polygon_temp_shapes:
            self.canvas.delete(shape)
        self.polygon_temp_shapes = []
        if self.polygon_preview_line is not None:
            self.canvas.delete(self.polygon_preview_line)
            self.polygon_preview_line = None
