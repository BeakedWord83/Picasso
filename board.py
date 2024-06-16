import tkinter as tk
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from shape_handler import ShapeHandler
from object_selector import ObjectSelector
from object_mover import ObjectMover
from object_editor import ObjectEditor
from fill_handler import FillHandler
from canvas_utils import CanvasUtils
from menu_handler import MenuHandler
from text_entry_handler import TextEntryHandler
from file_handler import FileHandler
from toolbox import Toolbox

if TYPE_CHECKING:
    from app import App


class Board:
    """
    A class representing the board where objects are drawn and manipulated.
    """

    CANVAS_SCROLLREGION = (-5000, -5000, 5000, 5000)

    def __init__(self, app: 'App', toolbox: 'Toolbox', loaded_fonts: Dict[tuple[str, int], Any]) -> None:
        """
        Initialize the Board.

        :param app: The application instance.
        :param toolbox: The toolbox instance.
        :param loaded_fonts: The loaded fonts dictionary.
        """
        self.app = app
        self.toolbox = toolbox
        self.loaded_fonts: Dict[tuple[str, int], Any] = loaded_fonts
        self.drawing: bool = False
        self.last_x: float = 0
        self.last_y: float = 0
        self.objects: List[int] = []
        self.menu: Optional[tk.Menu] = None
        self.text_entry: int = 0
        self.eraser_frame: Optional[int] = None
        self.right_click_x: float = 0
        self.right_click_y: float = 0

        self.x_scrollbar = tk.Scrollbar(self.app.get_root(), orient=tk.HORIZONTAL)
        self.y_scrollbar = tk.Scrollbar(self.app.get_root(), orient=tk.VERTICAL)
        self.canvas: tk.Canvas = tk.Canvas(self.app.get_root(), xscrollcommand=self.x_scrollbar.set,
                                           yscrollcommand=self.y_scrollbar.set)
        self.setup_canvas()
        self.shape_handler: ShapeHandler = ShapeHandler(self)
        self.object_selector: ObjectSelector = ObjectSelector(self)
        self.object_mover: ObjectMover = ObjectMover(self)
        self.object_editor: ObjectEditor = ObjectEditor(self)
        self.flood_fill: FillHandler = FillHandler(self)
        self.canvas_utils: CanvasUtils = CanvasUtils(self)
        self.text_entry_handler: TextEntryHandler = TextEntryHandler(self)
        self.file_handler: FileHandler = FileHandler(self)
        self.menu_handler: MenuHandler = MenuHandler(self)

        self.setup_bindings()
        self.on_tool_selected(self.toolbox.current_tool)
        self.toolbox.select_tool(self.toolbox.current_tool)

    def setup_canvas(self) -> None:
        """
        Set up the canvas and scrollbars.
        """
        self.x_scrollbar.config(command=self.canvas.xview)
        self.y_scrollbar.config(command=self.canvas.yview)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.config(scrollregion=Board.CANVAS_SCROLLREGION)

    def setup_bindings(self) -> None:
        """
        Set up the event bindings for the canvas.
        """
        self.canvas.bind("<Button-1>", self.handle_click_event)
        self.canvas.bind("<B1-Motion>", self.handle_drag_event)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<Button-3>", self.handle_right_click_event)
        self.toolbox.add_tool_selected_listener(self.on_tool_selected)

    def handle_click_event(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the click event on the canvas.

        :param event: The click event.
        """
        self.last_x = self.canvas.canvasx(event.x)
        self.last_y = self.canvas.canvasy(event.y)
        if self.toolbox.current_tool == "Select":
            current = self.canvas.find_withtag(tk.CURRENT)
            if current:
                clicked_object = current[0]
                if clicked_object not in self.object_selector.selected_objects:
                    self.object_selector.select_object(clicked_object)
                self.object_mover.start_move(event)
            else:
                self.object_selector.handle_select_tool_click(event)
        elif self.toolbox.current_tool == "Fill":
            self.flood_fill.fill_area(event)
        elif self.toolbox.current_tool == "Polygon":
            self.shape_handler.handle_polygon_click(event)
        elif self.toolbox.current_tool == "Text":
            self.text_entry_handler.create_text_entry(event)
        elif self.toolbox.current_tool == "Erase":
            self.canvas_utils.erase_objects(self.last_x, self.last_y)
        else:
            self.drawing = True
            if self.toolbox.current_tool in self.toolbox.shapes:
                self.shape_handler.start_shape()

    def handle_right_click_event(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the right-click event on the canvas.

        :param event: The right-click event.
        """
        self.right_click_x = self.canvas.canvasx(event.x)
        self.right_click_y = self.canvas.canvasy(event.y)
        current_object = self.canvas.find_withtag(tk.CURRENT)
        if not current_object:
            if self.object_selector.is_click_inside_selection_frame(event):
                if len(self.object_selector.selected_objects) == 1:
                    selected_object = self.object_selector.selected_objects[0]
                    item_type = self.canvas.type(selected_object)  # type: ignore
                    self.menu_handler.display_context_menu(event, item_type)
            elif self.object_editor.copied_object is not None:
                self.menu_handler.paste_context_menu(event)
        else:
            item_type = self.canvas.type(current_object[0])  # type: ignore
            if current_object[0] not in self.object_selector.selected_objects:
                self.object_selector.select_object(current_object[0])
            if len(self.object_selector.selected_objects) == 1:
                self.menu_handler.display_context_menu(event, item_type)

    def handle_drag_event(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Handle the drag event on the canvas.

        :param event: The drag event.
        """
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if self.toolbox.current_tool == "Move":
            self.object_mover.move_view(event)
        elif self.toolbox.current_tool == "Pen":
            self.shape_handler.draw_pen(canvas_x, canvas_y)
        elif self.toolbox.current_tool == "Select":
            if self.object_mover.is_moving:
                self.object_mover.continue_move(event)
            elif self.object_selector.is_click_inside_selection_frame(event):
                self.object_mover.start_move(event)
            else:
                self.object_selector.handle_select_tool_drag(event)
        elif self.toolbox.current_tool == "Erase":
            self.canvas_utils.erase_objects(canvas_x, canvas_y)
            self.canvas_utils.move_eraser_frame(event)
        elif self.toolbox.current_tool in self.toolbox.shapes:
            self.shape_handler.update_shape(event)

    def stop_drawing(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Stop the drawing process.

        :param event: The event that triggered the stop drawing.
        """
        if self.toolbox.current_tool in self.toolbox.shapes and self.drawing:
            self.shape_handler.finalize_shape()
        elif self.toolbox.current_tool == "Pen":
            self.shape_handler.pen_points = []
        elif self.toolbox.current_tool == "Select":
            self.object_selector.handle_select_tool_release(event)
            self.object_mover.end_move()

        if self.shape_handler.current_object:
            self.objects.append(self.shape_handler.current_object)

        self.drawing = False
        self.shape_handler.current_object = 0
        self.shape_handler.current_object_tag = ""

    def on_tool_selected(self, tool: str) -> None:
        """
        Handle the tool selection event.

        :param tool: The selected tool.
        """
        if tool != "Erase":
            self.canvas.unbind("<Motion>")
            if self.eraser_frame is not None:
                self.canvas.delete(self.eraser_frame)
                self.eraser_frame = None
        if tool == "Move":
            self.canvas.config(cursor="fleur")
        elif tool == "Pen":
            self.canvas.config(cursor="pencil")
        elif tool == "Select":
            self.canvas.config(cursor="hand2")
        elif tool == "Erase":
            self.canvas.config(cursor="X_cursor")
            self.canvas.bind("<Motion>", self.canvas_utils.move_eraser_frame)
        elif tool == "Fill":
            self.canvas.config(cursor="plus")
        elif tool == "Text":
            self.canvas.config(cursor="xterm")
        elif tool == "Return to Middle":
            self.canvas_utils.return_to_middle()
            self.toolbox.select_tool("Move")
        else:
            self.canvas.config(cursor="")
        self.object_selector.deselect_current_objects()
        if tool != "Polygon":
            self.shape_handler.clear_polygon_points()

    def destroy(self) -> None:
        """
        Destroy the board and its associated widgets.
        """
        self.canvas.destroy()
        self.x_scrollbar.destroy()
        self.y_scrollbar.destroy()
