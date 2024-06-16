import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board


class MenuHandler:
    """
    A class that handles the context menus for the board.
    """

    def __init__(self, board: 'Board') -> None:
        """
        Initialize the MenuHandler.

        :param board: The board instance.
        """
        self.board = board
        self.canvas = board.canvas
        self.object_editor = board.object_editor
        self.menu = tk.Menu(self.board.app.get_root())
        self.setup_menu()

    def setup_menu(self) -> None:
        """
        Set up the main menu for the application.
        """
        self.menu = tk.Menu(self.board.app.get_root())
        self.board.app.get_root().config(menu=self.menu)
        file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.board.file_handler.new_board)
        file_menu.add_command(label="Save", command=self.board.file_handler.save_board_dialog)
        file_menu.add_command(label="Open", command=self.board.file_handler.open_board_dialog)
        file_menu.add_command(label="Export", command=self.board.file_handler.export_board)

    def display_context_menu(self, event: 'tk.Event[tk.Misc]', item_type: str) -> None:
        """
        Display the appropriate context menu based on the item type.

        :param event: The event that triggered the context menu.
        :param item_type: The type of the item.
        """
        if item_type == "line":
            self.display_line_context_menu(event)
        elif item_type == "text":
            self.display_text_context_menu(event)
        elif item_type in ["rectangle", "oval", "polygon"]:
            self.display_shape_context_menu(event)

    def paste_context_menu(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Display the paste context menu.

        :param event: The event that triggered the context menu.
        """
        paste_menu = tk.Menu(self.canvas, tearoff=0)
        paste_menu.add_command(label="Paste", command=self.object_editor.paste_object_at_position)
        paste_menu.post(event.x_root, event.y_root)

    def display_line_context_menu(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Display the context menu for line objects.

        :param event: The event that triggered the context menu.
        """
        line_context_menu = tk.Menu(self.canvas, tearoff=0)
        line_context_menu.add_command(label="Copy", command=self.object_editor.copy_selected_object)
        line_context_menu.add_command(label="Delete", command=self.object_editor.delete_selected_object)
        line_context_menu.add_command(label="Change Color", command=self.object_editor.change_selected_object_color)
        line_context_menu.add_command(label="Change Width", command=self.object_editor.change_selected_object_width)
        line_context_menu.add_command(label="Move to Front", command=self.object_editor.move_selected_object_to_front)
        line_context_menu.add_command(label="Move to Back", command=self.object_editor.move_selected_object_to_back)
        line_context_menu.post(event.x_root, event.y_root)

    def display_text_context_menu(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Display the context menu for text objects.

        :param event: The event that triggered the context menu.
        """
        text_context_menu = tk.Menu(self.canvas, tearoff=0)
        text_context_menu.add_command(label="Copy", command=self.object_editor.copy_selected_object)
        text_context_menu.add_command(label="Delete", command=self.object_editor.delete_selected_object)
        text_context_menu.add_command(label="Change Color", command=self.object_editor.change_selected_object_color)
        text_context_menu.add_command(label="Change Font", command=self.object_editor.change_selected_object_font)
        text_context_menu.add_command(label="Change Font Size",
                                      command=self.object_editor.change_selected_object_font_size)
        text_context_menu.add_command(label="Move to Front", command=self.object_editor.move_selected_object_to_front)
        text_context_menu.add_command(label="Move to Back", command=self.object_editor.move_selected_object_to_back)
        text_context_menu.post(event.x_root, event.y_root)

    def display_shape_context_menu(self, event: 'tk.Event[tk.Misc]') -> None:
        """
        Display the context menu for shape objects.

        :param event: The event that triggered the context menu.
        """
        shape_context_menu = tk.Menu(self.canvas, tearoff=0)
        shape_context_menu.add_command(label="Copy", command=self.object_editor.copy_selected_object)
        shape_context_menu.add_command(label="Delete", command=self.object_editor.delete_selected_object)
        shape_context_menu.add_command(label="Change Color", command=self.object_editor.change_selected_object_color)
        shape_context_menu.add_command(label="Move to Front", command=self.object_editor.move_selected_object_to_front)
        shape_context_menu.add_command(label="Move to Back", command=self.object_editor.move_selected_object_to_back)
        shape_context_menu.post(event.x_root, event.y_root)
