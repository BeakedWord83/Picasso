import json
import os
import tkinter as tk
from tkinter import filedialog
from typing import Any, Dict, List, TYPE_CHECKING, Tuple

from PIL import Image, ImageDraw, ImageFont

from fallback_font import FallbackFont

if TYPE_CHECKING:
    from board import Board


class FileHandler:
    """
    A class that handles file operations for the board.
    """

    DEFAULT_DIR = "./boards"
    MAX_COORDINATE_VALUE = 5000

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the FileHandler.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.loaded_fonts = board.loaded_fonts

    def new_board(self) -> None:
        """
        Create a new board by clearing the canvas and resetting the objects.
        """
        self.canvas.delete("all")
        self.board.objects = []
        self.board.drawing = False
        self.board.canvas_utils.return_to_middle()

    def save_board_dialog(self) -> None:
        """
        Open a file dialog to save the board state to a file.
        """
        if not os.path.exists(FileHandler.DEFAULT_DIR):
            os.makedirs(FileHandler.DEFAULT_DIR)

        filename = filedialog.asksaveasfilename(initialdir=FileHandler.DEFAULT_DIR, defaultextension=".pcso",
                                                filetypes=[("Picasso Board", "*.pcso")])
        if filename:
            self.save_board(filename)

    def open_board_dialog(self) -> None:
        """
        Open a file dialog to load a board state from a file.
        """
        filename = tk.filedialog.askopenfilename(initialdir=FileHandler.DEFAULT_DIR, defaultextension=".pcso", filetypes=[("Picasso Board", "*.pcso")])
        if filename:
            self.load_board(filename)

    def save_board(self, filename: str) -> None:
        """
        Save the current board state to a file.

        :param filename: The name of the file to save the board state to.
        """
        objects_state = self._get_objects_state()
        board_state = {
            'objects': objects_state,
        }

        with open(filename, 'w') as f:
            json.dump(board_state, f)

    def _get_objects_state(self) -> List[Dict[str, Any]]:
        """
        Get the state of all objects on the canvas.

        :return: A list of object states.
        """
        objects_state: List[Dict[str, Any]] = []
        for obj in self.board.objects:
            item_type = self.canvas.type(obj)  # type: ignore
            obj_state: Dict[str, Any] = {
                'type': item_type,
                'coords': self.canvas.coords(obj),
                'fill': self.canvas.itemcget(obj, 'fill'),  # type: ignore
                'width': self.canvas.itemcget(obj, 'width'),  # type: ignore
                'z-index': self.canvas.find_all().index(obj),
            }
            if item_type not in ["line", "text"]:
                obj_state['outline'] = self.canvas.itemcget(obj, 'outline')  # type: ignore
            if item_type == "text":
                obj_state['font'] = self.canvas.itemcget(obj, 'font')  # type: ignore
                obj_state['text'] = self.canvas.itemcget(obj, 'text')  # type: ignore
            objects_state.append(obj_state)
        return objects_state

    def load_objects(self, objects_state: List[Dict[str, Any]]) -> None:
        """
        Load the objects from the given objects state onto the canvas.

        :param objects_state: The state of the objects to be loaded.
        """
        sorted_objects_state = sorted(objects_state, key=lambda x: x['z-index'])
        for obj_state in sorted_objects_state:
            obj = self._create_object_from_state(obj_state)
            if obj != 0:
                self.canvas.itemconfig(obj, tags=f"object{len(self.board.objects)}")
            self.board.objects.insert(0, obj)

    def _create_object_from_state(self, obj_state: Dict[str, Any]) -> int:
        """
        Create an object on the canvas based on the given object state.

        :param obj_state: The state of the object to be created.
        :return: The ID of the created object.
        """
        obj: int = 0
        if obj_state['type'] == 'line':
            obj = self.canvas.create_line(*obj_state['coords'], fill=obj_state['fill'],
                                          width=obj_state['width'])
        elif obj_state['type'] == 'rectangle':
            obj = self.canvas.create_rectangle(*obj_state['coords'], fill=obj_state['fill'],
                                               outline=obj_state['outline'], width=obj_state['width'])
        elif obj_state['type'] == 'oval':
            obj = self.canvas.create_oval(*obj_state['coords'], fill=obj_state['fill'],
                                          outline=obj_state['outline'], width=obj_state['width'])
        elif obj_state['type'] == 'polygon':
            obj = self.canvas.create_polygon(*obj_state['coords'], fill=obj_state['fill'],
                                             outline=obj_state['outline'], width=obj_state['width'])
        elif obj_state['type'] == 'text':
            font_name, font_size = obj_state['font'].split()
            pyglet_font: Any = self.loaded_fonts.get((font_name, int(font_size)))
            if pyglet_font is None:
                pyglet_font = FallbackFont(int(font_size))
            obj = self.canvas.create_text(*obj_state['coords'], text=obj_state['text'],
                                          font=(pyglet_font.name, pyglet_font.size),
                                          fill=obj_state['fill'])
        return obj

    def load_board(self, filename: str) -> None:
        """
        Load a board state from a file.

        :param filename: The name of the file to load the board state from.
        """
        self.new_board()

        with open(filename, 'r') as f:
            board_state = json.load(f)

        self.load_objects(board_state['objects'])

    def export_board(self) -> None:
        """
        Export the board as an image file.
        """
        file_path = filedialog.asksaveasfilename(filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("GIF", "*.gif")])
        if file_path:
            self._export_board_as_image(file_path)

    def _export_board_as_image(self, file_path: str) -> None:
        """
        Export the board as an image file.

        :param file_path: The path of the file to save the exported image.
        """
        all_objects = self.canvas.find_all()
        min_x, min_y, max_x, max_y = self._get_board_dimensions(all_objects)

        width = int(max_x - min_x)
        height = int(max_y - min_y)

        image = Image.new("RGBA", (width, height), "white")
        drawable = ImageDraw.Draw(image)

        for obj in self.canvas.find_all():
            obj_tags = self.canvas.itemcget(obj, "tags")  # type: ignore
            if obj_tags in ["selection_frame", "eraser_frame"]:
                continue

            self._draw_object_on_image(obj, drawable, min_x, min_y)

        if file_path.lower().endswith(".jpg"):
            image = image.convert("RGB")

        image.save(file_path)

    def _get_board_dimensions(self, all_objects: Tuple[int, ...]) -> Tuple[float, float, float, float]:
        """
        Get the dimensions of the board based on the objects on the canvas.

        :param all_objects: A list of all objects on the canvas.
        :return: A tuple containing the minimum and maximum coordinates of the board.
        """
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for obj in all_objects:
            obj_tags = self.canvas.itemcget(obj, "tags")  # type: ignore
            if obj_tags in ["selection_frame", "eraser_frame"]:
                continue
            bbox = self.canvas.bbox(obj)
            min_x = min(min_x, bbox[0])
            min_y = min(min_y, bbox[1])
            max_x = max(max_x, bbox[2])
            max_y = max(max_y, bbox[3])

        if min_x == float('inf') or min_y == float('inf') or max_x == float('-inf') or max_y == float('-inf'):
            min_x, min_y = -100, -100
            max_x, max_y = 100, 100

        min_x = max(min_x, -FileHandler.MAX_COORDINATE_VALUE)
        min_y = max(min_y, -FileHandler.MAX_COORDINATE_VALUE)
        max_x = min(max_x, FileHandler.MAX_COORDINATE_VALUE)
        max_y = min(max_y, FileHandler.MAX_COORDINATE_VALUE)

        return min_x, min_y, max_x, max_y

    def _draw_object_on_image(self, obj: int, drawable: ImageDraw.Draw, min_x: float, min_y: float) -> None:
        """
        Draw an object on the image.

        :param obj: The ID of the object to be drawn.
        :param drawable: The ImageDraw object for drawing on the image.
        :param min_x: The minimum x-coordinate of the board.
        :param min_y: The minimum y-coordinate of the board.
        """
        item_type = self.canvas.type(obj)  # type: ignore
        coords = self.canvas.coords(obj)

        adjusted_coords = [coord - min_x if i % 2 == 0 else coord - min_y for i, coord in enumerate(coords)]

        width = self.canvas.itemcget(obj, "width")  # type: ignore
        if isinstance(width, tuple):
            width = width[0]
        elif isinstance(width, str):
            width = int(float(width))

        fill_color = self.canvas.itemcget(obj, "fill")  # type: ignore
        if item_type == "rectangle":
            outline_color = self.canvas.itemcget(obj, "outline")  # type: ignore
            coords_tuple = (adjusted_coords[0], adjusted_coords[1], adjusted_coords[2], adjusted_coords[3])
            drawable.rectangle(coords_tuple, fill=fill_color, outline=outline_color, width=width)
        elif item_type == "oval":
            outline_color = self.canvas.itemcget(obj, "outline")  # type: ignore
            drawable.ellipse(adjusted_coords, fill=fill_color, outline=outline_color, width=width)
        elif item_type == "polygon":
            drawable.polygon(adjusted_coords, fill=fill_color, width=width)
        elif item_type == "line":
            drawable.line(adjusted_coords, fill=fill_color, width=width)
        elif item_type == "text":
            self._draw_text_on_image(obj, drawable, adjusted_coords, fill_color)

    def _draw_text_on_image(self, obj: int, drawable: ImageDraw.Draw, adjusted_coords: List[float], fill_color: str) -> None:
        """
        Draw a text object on the image.

        :param obj: The ID of the text object to be drawn.
        :param drawable: The ImageDraw object for drawing on the image.
        :param adjusted_coords: The adjusted coordinates of the text object.
        :param fill_color: The fill color of the text object.
        """
        text = self.canvas.itemcget(obj, "text")  # type: ignore
        font_name, font_size = self.canvas.itemcget(obj, "font").split()  # type: ignore
        font_path = os.path.join("fonts", font_name + ".ttf")
        try:
            font = ImageFont.truetype(font_path, int(font_size))
        except (OSError, IOError):
            font_path = os.path.join("fonts", "Arial.ttf")
            font = ImageFont.truetype(font_path, int(font_size))

        text_width, text_height = font.getbbox(text)[2:4]

        text_x = adjusted_coords[0] - text_width // 2
        text_y = adjusted_coords[1] - text_height // 2

        drawable.text((text_x, text_y), text, fill=fill_color, font=font)
