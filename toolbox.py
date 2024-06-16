import tkinter as tk
from tkinter import colorchooser
from typing import List, Dict, Callable, TYPE_CHECKING

from PIL import Image, ImageTk

from button_item import ButtonItem

if TYPE_CHECKING:
    from app import App


class Toolbox:
    """
    A class representing the toolbox in the application.
    """

    TOOL_SELECT = "Select"
    TOOL_PEN = "Pen"
    TOOL_ERASE = "Erase"
    TOOL_MOVE = "Move"
    TOOL_FILL = "Fill"
    TOOL_SHAPES = "Shapes"
    TOOL_TEXT = "Text"

    SHAPE_RECTANGLE = "Rectangle"
    SHAPE_TRIANGLE = "Triangle"
    SHAPE_CIRCLE = "Circle"
    SHAPE_LINE = "Line"
    SHAPE_POLYGON = "Polygon"

    DEFAULT_PEN_WIDTH = 5
    DEFAULT_PEN_COLOR = "black"
    DEFAULT_FILL_COLOR = "black"
    DEFAULT_ERASER_WIDTH = 20
    DEFAULT_TEXT_COLOR = "black"
    DEFAULT_TEXT_FONT_NAME = "Arial"
    DEFAULT_TEXT_FONT_SIZE = 12

    TOOL_ICON_SIZE = (50, 50)

    def __init__(self, parent: 'App') -> None:
        """
        Initialize the Toolbox.

        :param parent: The parent application.
        """
        self.frame = tk.Frame(parent.get_root())
        self.current_tool: str = Toolbox.TOOL_PEN
        self.tools: List[str] = [Toolbox.TOOL_SELECT, Toolbox.TOOL_PEN, Toolbox.TOOL_ERASE, Toolbox.TOOL_MOVE, Toolbox.TOOL_FILL, Toolbox.TOOL_SHAPES, Toolbox.TOOL_TEXT]
        self.tool_icons: Dict[str, str] = {
            Toolbox.TOOL_SELECT: "images/select_icon.png",
            Toolbox.TOOL_PEN: "images/pen_icon.png",
            Toolbox.TOOL_ERASE: "images/eraser_icon.png",
            Toolbox.TOOL_MOVE: "images/move_icon.png",
            Toolbox.TOOL_FILL: "images/fill_icon.png",
            Toolbox.TOOL_SHAPES: "images/shapes_icon.png",
            Toolbox.TOOL_TEXT: "images/text_icon.png"
        }
        self.shapes: List[str] = [Toolbox.SHAPE_RECTANGLE, Toolbox.SHAPE_TRIANGLE, Toolbox.SHAPE_CIRCLE, Toolbox.SHAPE_LINE, Toolbox.SHAPE_POLYGON]
        self.shapes_icons: Dict[str, str] = {
            Toolbox.SHAPE_RECTANGLE: "images/rectangle_icon.png",
            Toolbox.SHAPE_TRIANGLE: "images/triangle_icon.png",
            Toolbox.SHAPE_CIRCLE: "images/circle_icon.png",
            Toolbox.SHAPE_LINE: "images/line_icon.png",
            Toolbox.SHAPE_POLYGON: "images/polygon_icon.png"
        }
        self.tool_selected_listeners: List[Callable[[str], None]] = []
        self.pen_width: int = Toolbox.DEFAULT_PEN_WIDTH
        self.pen_color: str = Toolbox.DEFAULT_PEN_COLOR
        self.fill_color: str = Toolbox.DEFAULT_FILL_COLOR
        self.eraser_width: int = Toolbox.DEFAULT_ERASER_WIDTH
        self.text_color: str = Toolbox.DEFAULT_TEXT_COLOR
        self.text_font_name: str = Toolbox.DEFAULT_TEXT_FONT_NAME
        self.text_font_size: int = Toolbox.DEFAULT_TEXT_FONT_SIZE
        self.frame.pack()
        self.tool_buttons: Dict[str, ButtonItem] = {}

        self._create_tool_buttons()

    def _create_tool_buttons(self) -> None:
        """
        Create buttons for each tool.
        """
        for tool in self.tools:
            tool_frame = tk.Frame(self.frame)
            tool_frame.pack(side=tk.LEFT)

            image = Image.open(self.tool_icons[tool])
            image = image.resize(Toolbox.TOOL_ICON_SIZE, Image.BICUBIC)
            icon = ImageTk.PhotoImage(image)
            button = tk.Button(tool_frame, image=icon, command=lambda x=tool: self.select_tool(x))  # type: ignore
            button_item = ButtonItem(button, icon)
            button.pack()
            self.tool_buttons[tool] = button_item

            self._create_tool_specific_widgets(tool, tool_frame)

    def _create_tool_specific_widgets(self, tool: str, tool_frame: tk.Frame) -> None:
        """
        Create tool-specific widgets for each tool.

        :param tool: The tool name.
        :param tool_frame: The frame for the tool-specific widgets.
        """
        if tool == Toolbox.TOOL_PEN:
            self.pen_button = self.tool_buttons[tool].button
            self.color_button = tk.Button(tool_frame, text="Color", command=self.choose_pen_color)
            self.pen_width_scale = tk.Scale(tool_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.set_pen_width)
            self.pen_width_scale.set(self.pen_width)
            self.pen_width_scale.pack_forget()
            self.color_button.pack_forget()
        elif tool == Toolbox.TOOL_MOVE:
            self.move_frame = tk.Frame(tool_frame)
            self.return_to_middle_button = tk.Button(self.move_frame, text="Return to Middle", command=self.return_to_middle)
            self.return_to_middle_button.pack()
            self.move_frame.pack_forget()
        elif tool == Toolbox.TOOL_ERASE:
            self.eraser_button = self.tool_buttons[tool].button
            self.eraser_width_scale = tk.Scale(tool_frame, from_=5, to=50, orient=tk.HORIZONTAL, command=self.set_eraser_width)
            self.eraser_width_scale.set(self.eraser_width)
            self.eraser_width_scale.pack_forget()
        elif tool == Toolbox.TOOL_SHAPES:
            self.shapes_frame = tk.Frame(tool_frame)
            for shape in self.shapes:
                shape_image = Image.open(self.shapes_icons[shape])
                shape_image = shape_image.resize(Toolbox.TOOL_ICON_SIZE, Image.BICUBIC)
                shape_icon = ImageTk.PhotoImage(shape_image)
                shape_button = tk.Button(self.shapes_frame, image=shape_icon, command=lambda x=shape: self.select_tool(x))  # type: ignore
                shape_button_item = ButtonItem(shape_button, shape_icon)
                shape_button.pack(side=tk.LEFT)
                self.tool_buttons[shape] = shape_button_item
            self.shapes_frame.pack_forget()
        elif tool == Toolbox.TOOL_TEXT:
            self.text_button = self.tool_buttons[tool].button
            self.font_var = tk.StringVar()
            self.font_dropdown = tk.OptionMenu(tool_frame, self.font_var, "Arial", "Georgia", "Calibri", "Courier", "Verdana", command=self.update_font_name)
            self.font_var.set("Arial")
            self.font_dropdown.pack_forget()
            self.size_var = tk.StringVar()
            self.size_dropdown = tk.OptionMenu(tool_frame, self.size_var, "8", "10", "12", "14", "16", "18", "20", "24", "28", "32", command=self.update_font_size)
            self.size_var.set("12")
            self.size_dropdown.pack_forget()
            self.text_color_button = tk.Button(tool_frame, text="Color", command=self.choose_text_color)
            self.text_color_button.pack_forget()

    def choose_pen_color(self) -> None:
        """
        Open a color chooser dialog to select the pen color.
        """
        color = colorchooser.askcolor()[1]
        if color is not None:
            self.pen_color = color

    def choose_fill_color(self) -> None:
        """
        Open a color chooser dialog to select the fill color.
        """
        color = colorchooser.askcolor()[1]
        if color is not None:
            self.fill_color = color

    def select_tool(self, tool: str) -> None:
        """
        Select a tool and update the UI accordingly.

        :param tool: The selected tool.
        """
        self.current_tool = tool
        self._reset_tool_button_colors()
        self.tool_buttons[tool].button.configure(bg="yellow")
        self._show_hide_tool_specific_widgets(tool)
        for listener in self.tool_selected_listeners:
            listener(tool)

    def _reset_tool_button_colors(self) -> None:
        """
        Reset the background color of all tool buttons to the default color.
        """
        for button_item in self.tool_buttons.values():
            button_item.button.configure(bg="white")

    def _show_hide_tool_specific_widgets(self, tool: str) -> None:
        """
        Show or hide the appropriate widgets based on the selected tool.

        :param tool: The selected tool.
        """
        self._hide_all_tool_specific_widgets()

        if tool == Toolbox.TOOL_PEN:
            self.pen_width_scale.pack()
            self.color_button.pack()
        elif tool == Toolbox.TOOL_ERASE:
            self.eraser_width_scale.pack()
        elif tool == Toolbox.TOOL_FILL:
            self.choose_fill_color()
        elif tool == Toolbox.TOOL_SHAPES:
            self.shapes_frame.pack()
        elif tool in self.shapes:
            self.shapes_frame.pack()
            for shape_item in self.tool_buttons.values():
                shape_item.button.configure(bg="white")
            self.tool_buttons[tool].button.configure(bg="yellow")
        elif tool == Toolbox.TOOL_TEXT:
            self.font_dropdown.pack()
            self.size_dropdown.pack()
            self.text_color_button.pack()
        elif tool == Toolbox.TOOL_MOVE:
            self.move_frame.pack()

    def _hide_all_tool_specific_widgets(self) -> None:
        """
        Hide all tool-specific widgets.
        """
        self.pen_width_scale.pack_forget()
        self.color_button.pack_forget()
        self.eraser_width_scale.pack_forget()
        self.shapes_frame.pack_forget()
        self.font_dropdown.pack_forget()
        self.size_dropdown.pack_forget()
        self.text_color_button.pack_forget()
        self.move_frame.pack_forget()

    def set_eraser_width(self, width: str) -> None:
        """
        Set the eraser width.

        :param width: The eraser width.
        """
        self.eraser_width = int(width)

    def update_font_name(self, _: tk.StringVar) -> None:
        """
        Update the text font name based on the selected value.

        :param _: The selected font name (unused).
        """
        self.text_font_name = self.font_var.get()

    def update_font_size(self, _: tk.StringVar) -> None:
        """
        Update the text font size based on the selected value.

        :param _: The selected font size (unused).
        """
        self.text_font_size = int(self.size_var.get())

    def choose_text_color(self) -> None:
        """
        Open a color chooser dialog to select the text color.
        """
        color = colorchooser.askcolor()[1]
        if color is not None:
            self.text_color = color

    def add_tool_selected_listener(self, listener: Callable[[str], None]) -> None:
        """
        Add a listener to be called when a tool is selected.

        :param listener: The listener function to add.
        """
        self.tool_selected_listeners.append(listener)

    def set_pen_width(self, width: str) -> None:
        """
        Set the pen width.

        :param width: The pen width.
        """
        self.pen_width = int(width)

    def return_to_middle(self) -> None:
        """
        Notify the listeners to return to the middle.
        """
        for listener in self.tool_selected_listeners:
            listener("Return to Middle")
