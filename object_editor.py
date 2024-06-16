import tkinter as tk
from tkinter import colorchooser
from typing import Optional, Dict, Any, TYPE_CHECKING

from font_dialog import FontDialog
from font_size_dialog import FontSizeDialog
from width_dialog import WidthDialog

if TYPE_CHECKING:
    from board import Board


class ObjectEditor:
    """
    A class that handles object editing functionality for the board.
    """

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the ObjectEditor.

        :param board: The board instance.
        """
        self.board = board
        self.canvas: tk.Canvas = board.canvas
        self.toolbox = board.toolbox
        self.object_selector = board.object_selector
        self.copied_object: Optional[Dict[str, Any]] = None

    def copy_selected_object(self) -> None:
        """
        Copy the selected object.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            # Copy the selected object
            copied_object_coords = self.canvas.coords(selected_object)
            copied_object_type = self.canvas.type(selected_object)  # type: ignore
            copied_object_fill = self.canvas.itemcget(selected_object, 'fill')  # type: ignore
            copied_object_width = self.canvas.itemcget(selected_object, 'width')  # type: ignore

            copied_object_outline = None
            if copied_object_type in ['rectangle', 'oval']:
                copied_object_outline = self.canvas.itemcget(selected_object, 'outline')  # type: ignore

            copied_object_text = None
            copied_object_font = None
            if copied_object_type == 'text':
                copied_object_text = self.canvas.itemcget(selected_object, 'text')  # type: ignore
                copied_object_font = self.canvas.itemcget(selected_object, 'font')  # type: ignore

            self.copied_object = {
                'coords': copied_object_coords,
                'type': copied_object_type,
                'fill': copied_object_fill,
                'outline': copied_object_outline,
                'width': copied_object_width,
                'text': copied_object_text,
                'font': copied_object_font
            }

    def paste_object_at_position(self) -> None:
        """
        Paste the copied object at the current position.
        """
        if self.copied_object is not None:
            # Paste the copied object
            copied_object_coords = self.copied_object['coords']
            copied_object_type = self.copied_object['type']
            copied_object_fill = self.copied_object['fill']
            copied_object_width = self.copied_object['width']
            copied_object_outline = self.copied_object['outline']

            if copied_object_type == 'line':
                self.adjust_copied_object_center(copied_object_coords)

            elif copied_object_type == 'text':
                # Adjust the coordinates to the right-click position
                copied_object_coords[0] = self.board.right_click_x
                copied_object_coords[1] = self.board.right_click_y

            elif copied_object_type == 'polygon':
                self.adjust_copied_object_center(copied_object_coords)
            else:
                # Calculate the width and height of the copied object
                width = copied_object_coords[2] - copied_object_coords[0]
                height = copied_object_coords[3] - copied_object_coords[1]

                # Adjust the coordinates to the right-click position
                copied_object_coords[0] = self.board.right_click_x - width / 2
                copied_object_coords[1] = self.board.right_click_y - height / 2
                copied_object_coords[2] = self.board.right_click_x + width / 2
                copied_object_coords[3] = self.board.right_click_y + height / 2

            new_object: Optional[int] = None  # Initialize the new_object variable
            if copied_object_type == 'rectangle':
                new_object = self.canvas.create_rectangle(*copied_object_coords, fill=copied_object_fill,
                                                          outline=copied_object_outline, width=copied_object_width,
                                                          tags=(f"object{len(self.board.objects)}",))
            elif copied_object_type == 'oval':
                new_object = self.canvas.create_oval(*copied_object_coords, fill=copied_object_fill,
                                                     outline=copied_object_outline, width=copied_object_width,
                                                     tags=(f"object{len(self.board.objects)}",))
            elif copied_object_type == 'line':
                new_object = self.canvas.create_line(*copied_object_coords, fill=copied_object_fill,
                                                     width=copied_object_width,
                                                     tags=(f"object{len(self.board.objects)}",))
            elif copied_object_type == 'text':
                copied_object_text = self.copied_object['text']
                copied_object_font = self.copied_object['font']
                new_object = self.canvas.create_text(*copied_object_coords, text=copied_object_text,
                                                     font=copied_object_font, fill=copied_object_fill,
                                                     tags=(f"object{len(self.board.objects)}",))
            elif copied_object_type == 'polygon':
                new_object = self.canvas.create_polygon(*copied_object_coords, fill=copied_object_fill,
                                                        outline=copied_object_outline, width=copied_object_width,
                                                        tags=(f"object{len(self.board.objects)}",))

            if new_object is not None:
                self.board.objects.append(new_object)

    def adjust_copied_object_center(self, copied_object_coords: Any) -> None:
        copied_object_center_x = sum(
            copied_object_coords[i] for i in range(0, len(copied_object_coords), 2)) / (
                                         len(copied_object_coords) // 2)
        copied_object_center_y = sum(
            copied_object_coords[i] for i in range(1, len(copied_object_coords), 2)) / (
                                         len(copied_object_coords) // 2)

        # Calculate the difference between the center of the copied polygon and the right-click position
        dx = self.board.right_click_x - copied_object_center_x
        dy = self.board.right_click_y - copied_object_center_y

        # Adjust the coordinates of the pasted polygon
        for i in range(0, len(copied_object_coords), 2):
            copied_object_coords[i] += dx
            copied_object_coords[i + 1] += dy

    def delete_selected_object(self) -> None:
        """
        Delete the selected object.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            self.canvas.delete(selected_object)
            self.canvas.delete("selection_frame")
            self.board.objects.remove(selected_object)
            self.object_selector.selected_objects = []
            self.object_selector.selection_frame = None

    def change_selected_object_color(self) -> None:
        """
        Change the color of the selected object.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            color = colorchooser.askcolor()[1]
            if color is not None:
                item_type = self.canvas.type(selected_object)  # type: ignore
                if item_type in ["line", "text", "polygon"]:
                    self.canvas.itemconfig(selected_object, fill=color)
                else:
                    self.canvas.itemconfig(selected_object, fill=color, outline=color)
                if item_type == "text":
                    self.toolbox.text_color = color

    def change_selected_object_width(self) -> None:
        """
        Change the width of the selected object.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            selected_object_width = self.canvas.itemcget(selected_object, 'width')  # type: ignore
            dialog = WidthDialog(self.board.app.get_root(), selected_object_width)
            self.board.app.get_root().wait_window(dialog)
            width = dialog.result
            if width is not None:
                self.canvas.itemconfig(selected_object, width=width)

    def change_selected_object_font(self) -> None:
        """
        Change the font of the selected object.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            selected_object_type = self.canvas.type(selected_object)  # type: ignore
            if selected_object_type == "text":
                current_font = self.canvas.itemcget(selected_object, "font")  # type: ignore
                font_name, font_size = current_font.split()
                font_dialog = FontDialog(self.board.app.get_root(), font_name)
                self.board.app.get_root().wait_window(font_dialog)
                if font_dialog.result:
                    self.canvas.itemconfig(selected_object, font=(font_dialog.result, font_size))

    def change_selected_object_font_size(self) -> None:
        """
        Change the font size of the selected object.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            selected_object_type = self.canvas.type(selected_object)  # type: ignore
            if selected_object_type == "text":
                current_font = self.canvas.itemcget(selected_object, "font")  # type: ignore
                font_parts = current_font.split()
                font_name = " ".join(font_parts[:-1])  # Join all parts except the last one
                font_size = font_parts[-1]  # Get the last part as the font size
                size_dialog = FontSizeDialog(self.board.app.get_root(), font_size)
                self.board.app.get_root().wait_window(size_dialog)
                if size_dialog.result:
                    self.canvas.itemconfig(selected_object, font=(font_name, size_dialog.result))
                    self.object_selector.draw_selection_frame()

    def move_selected_object_to_front(self) -> None:
        """
        Move the selected object to the front.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            self.canvas.tag_raise(selected_object)

    def move_selected_object_to_back(self) -> None:
        """
        Move the selected object to the back.
        """
        if self.object_selector.selected_objects:
            selected_object = self.object_selector.selected_objects[0]
            self.canvas.tag_lower(selected_object)
