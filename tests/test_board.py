import pytest
import tkinter as tk
from unittest.mock import Mock, patch

from board import Board


@pytest.fixture(scope='session')
def root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def board(root):
    app = Mock()
    app.get_root.return_value = root
    toolbox = Mock()
    loaded_fonts = {}
    board = Board(app, toolbox, loaded_fonts)
    board.object_mover = Mock()
    board.shape_handler = Mock()
    yield board
    board.destroy()


def test_setup_canvas(board):
    assert isinstance(board.x_scrollbar, tk.Scrollbar)
    assert isinstance(board.y_scrollbar, tk.Scrollbar)
    assert isinstance(board.canvas, tk.Canvas)
    assert board.canvas.cget('xscrollcommand') is not None
    assert board.canvas.cget('yscrollcommand') is not None


def test_setup_canvas_config(board, root):
    board.setup_canvas()
    assert board.canvas.master == root
    assert board.x_scrollbar.master == root
    assert board.y_scrollbar.master == root
    assert board.canvas.cget('scrollregion') == '-5000 -5000 5000 5000'


@patch('board.Board.handle_click_event')
@patch('board.Board.handle_drag_event')
@patch('board.Board.stop_drawing')
@patch('board.Board.handle_right_click_event')
def test_setup_bindings(mock_handle_right_click_event, mock_stop_drawing, mock_handle_drag_event,
                        mock_handle_click_event, board):
    board.setup_bindings()
    board.handle_click_event(Mock())
    mock_handle_click_event.assert_called_once()
    board.handle_drag_event(Mock())
    mock_handle_drag_event.assert_called_once()
    board.stop_drawing(Mock())
    mock_stop_drawing.assert_called_once()
    board.handle_right_click_event(Mock())
    mock_handle_right_click_event.assert_called_once()


def test_handle_click_event(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Select"
    board.handle_click_event(event)
    assert board.last_x == board.canvas.canvasx(event.x)
    assert board.last_y == board.canvas.canvasy(event.y)


def test_handle_click_event_with_different_tools(board):
    event = Mock()
    event.x = 100
    event.y = 100

    # Test for "Fill" tool
    board.toolbox.current_tool = "Fill"
    board.flood_fill.fill_area = Mock()
    board.handle_click_event(event)
    board.flood_fill.fill_area.assert_called_once_with(event)

    # Test for "Polygon" tool
    board.toolbox.current_tool = "Polygon"
    board.shape_handler.handle_polygon_click = Mock()
    board.handle_click_event(event)
    board.shape_handler.handle_polygon_click.assert_called_once_with(event)

    # Test for "Text" tool
    board.toolbox.current_tool = "Text"
    board.text_entry_handler.create_text_entry = Mock()
    board.handle_click_event(event)
    board.text_entry_handler.create_text_entry.assert_called_once_with(event)

    # Test for "Erase" tool
    board.toolbox.current_tool = "Erase"
    board.canvas_utils.erase_objects = Mock()
    board.handle_click_event(event)
    board.canvas_utils.erase_objects.assert_called_once_with(board.last_x, board.last_y)


def test_handle_click_event_select_tool(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Select"
    board.canvas.find_withtag = Mock(return_value=[1])
    board.object_selector.select_object = Mock()
    board.object_mover.start_move = Mock()

    board.handle_click_event(event)

    board.object_selector.select_object.assert_called_once_with(1)
    board.object_mover.start_move.assert_called_once_with(event)


def test_handle_click_event_shape_tool(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Rectangle"
    board.toolbox.shapes = ["Rectangle", "Circle", "Triangle"]  # Set toolbox.shapes to a list
    board.shape_handler.start_shape = Mock()

    board.handle_click_event(event)

    assert board.drawing
    board.shape_handler.start_shape.assert_called_once()


def test_handle_right_click_event(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.handle_right_click_event(event)
    assert board.right_click_x == board.canvas.canvasx(event.x)
    assert board.right_click_y == board.canvas.canvasy(event.y)

    # Test when no object is clicked
    board.canvas.find_withtag = Mock(return_value=[])
    board.object_selector.is_click_inside_selection_frame = Mock(return_value=False)
    board.object_editor.copied_object = None
    board.menu_handler.display_context_menu = Mock()
    board.menu_handler.paste_context_menu = Mock()
    board.handle_right_click_event(event)
    board.menu_handler.display_context_menu.assert_not_called()
    board.menu_handler.paste_context_menu.assert_not_called()

    # Test when an object is clicked
    board.canvas.find_withtag = Mock(return_value=[1])
    board.canvas.gettags = Mock(return_value=["object0"])
    board.canvas.type = Mock(return_value="rectangle")

    def select_object_side_effect(obj):
        board.object_selector.selected_objects.append(obj)

    board.object_selector.select_object = Mock(side_effect=select_object_side_effect)
    board.menu_handler.display_context_menu = Mock()
    board.handle_right_click_event(event)
    board.object_selector.select_object.assert_called_once_with(1)
    board.menu_handler.display_context_menu.assert_called_once_with(event, "rectangle")


def test_handle_right_click_event_selected_object(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.canvas.find_withtag = Mock(return_value=[1])
    board.canvas.gettags = Mock(return_value=["object0"])
    board.canvas.type = Mock(return_value="rectangle")
    board.object_selector.selected_objects = [1]
    board.menu_handler.display_context_menu = Mock()

    board.handle_right_click_event(event)

    board.menu_handler.display_context_menu.assert_called_once_with(event, "rectangle")


def test_handle_right_click_event_click_inside_selection_frame(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.canvas.find_withtag = Mock(return_value=[])
    board.object_selector.is_click_inside_selection_frame = Mock(return_value=True)
    board.object_selector.selected_objects = [1]
    board.canvas.type = Mock(return_value="rectangle")
    board.menu_handler.display_context_menu = Mock()

    board.handle_right_click_event(event)

    board.menu_handler.display_context_menu.assert_called_once_with(event, "rectangle")


def test_handle_right_click_event_copied_object(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.canvas.find_withtag = Mock(return_value=[])
    board.object_selector.is_click_inside_selection_frame = Mock(return_value=False)
    board.object_editor.copied_object = "copied_object"
    board.menu_handler.paste_context_menu = Mock()

    board.handle_right_click_event(event)

    board.menu_handler.paste_context_menu.assert_called_once_with(event)


def test_handle_drag_event(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Move"
    board.handle_drag_event(event)
    assert board.object_mover.move_view.call_count == 1
    assert board.object_mover.move_view.call_args == ((event,),)


def test_handle_drag_event_pen_tool(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Pen"
    board.shape_handler.draw_pen = Mock()

    board.handle_drag_event(event)

    board.shape_handler.draw_pen.assert_called_once_with(board.canvas.canvasx(event.x), board.canvas.canvasy(event.y))


def test_handle_drag_event_select_tool_moving(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Select"
    board.object_mover.is_moving = True
    board.object_mover.continue_move = Mock()

    board.handle_drag_event(event)

    board.object_mover.continue_move.assert_called_once_with(event)


def test_handle_drag_event_select_tool_resizing(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Select"
    board.object_mover.is_moving = False
    board.object_selector.is_click_inside_selection_frame = Mock(return_value=True)
    board.object_mover.start_move = Mock()

    board.handle_drag_event(event)

    board.object_mover.start_move.assert_called_once_with(event)


def test_handle_drag_event_select_tool_dragging(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Select"
    board.object_mover.is_moving = False
    board.object_selector.is_click_inside_selection_frame = Mock(return_value=False)
    board.object_selector.handle_select_tool_drag = Mock()

    board.handle_drag_event(event)

    board.object_selector.handle_select_tool_drag.assert_called_once_with(event)


def test_handle_drag_event_erase_tool(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Erase"
    board.canvas_utils.erase_objects = Mock()
    board.canvas_utils.move_eraser_frame = Mock()

    board.handle_drag_event(event)

    board.canvas_utils.erase_objects.assert_called_once_with(board.canvas.canvasx(event.x),
                                                             board.canvas.canvasy(event.y))
    board.canvas_utils.move_eraser_frame.assert_called_once_with(event)


def test_handle_drag_event_shape_tool(board):
    event = Mock()
    event.x = 100
    event.y = 100
    board.toolbox.current_tool = "Rectangle"
    board.toolbox.shapes = ["Rectangle", "Circle", "Triangle"]  # Set toolbox.shapes to a list
    board.shape_handler.update_shape = Mock()

    board.handle_drag_event(event)

    board.shape_handler.update_shape.assert_called_once_with(event)


def test_stop_drawing(board):
    event = Mock()
    board.toolbox.shapes = ["Rectangle"]
    board.toolbox.current_tool = "Rectangle"
    board.drawing = True
    board.stop_drawing(event)
    assert board.shape_handler.finalize_shape.call_count == 1
    assert not board.drawing
    assert board.shape_handler.current_object == 0
    assert board.shape_handler.current_object_tag == ""


def test_stop_drawing_shape_tool(board):
    event = Mock()
    board.toolbox.shapes = ["Rectangle"]
    board.toolbox.current_tool = "Rectangle"
    board.drawing = True
    board.shape_handler.finalize_shape = Mock()

    board.stop_drawing(event)

    board.shape_handler.finalize_shape.assert_called_once()
    assert not board.drawing
    assert board.shape_handler.current_object == 0
    assert board.shape_handler.current_object_tag == ""


def test_stop_drawing_pen_tool(board):
    event = Mock()
    board.toolbox.current_tool = "Pen"
    board.toolbox.shapes = ["Rectangle", "Circle", "Triangle"]  # Set toolbox.shapes to a list
    board.shape_handler.pen_points = [1, 2, 3]

    board.stop_drawing(event)

    assert board.shape_handler.pen_points == []


def test_stop_drawing_select_tool(board):
    event = Mock()
    board.toolbox.current_tool = "Select"
    board.toolbox.shapes = ["Rectangle", "Circle", "Triangle"]  # Set toolbox.shapes to a list
    board.object_selector.handle_select_tool_release = Mock()
    board.object_mover.end_move = Mock()

    board.stop_drawing(event)

    board.object_selector.handle_select_tool_release.assert_called_once_with(event)
    board.object_mover.end_move.assert_called_once()


def test_on_tool_selected(board):
    # Test for "Return to Middle" tool
    board.canvas_utils.return_to_middle = Mock()
    board.toolbox.select_tool = Mock()
    board.on_tool_selected("Return to Middle")
    board.canvas_utils.return_to_middle.assert_called_once()
    board.toolbox.select_tool.assert_called_once_with("Move")

    # Test for "Polygon" tool
    board.shape_handler.clear_polygon_points = Mock()
    board.on_tool_selected("Polygon")
    board.shape_handler.clear_polygon_points.assert_not_called()

    # Test for "Erase" tool
    board.canvas.config = Mock()
    board.canvas.bind = Mock()
    board.canvas_utils.move_eraser_frame = Mock()
    board.on_tool_selected("Erase")
    board.canvas.bind.assert_called_once_with("<Motion>", board.canvas_utils.move_eraser_frame)

    # Test for other tools
    for tool in ["Move", "Pen", "Select", "Fill", "Text"]:
        board.canvas.config = Mock()
        board.object_selector.deselect_current_objects = Mock()
        board.on_tool_selected(tool)
        board.canvas.config.assert_called_once()
        board.object_selector.deselect_current_objects.assert_called_once()


def test_on_tool_selected_move_tool(board):
    board.canvas.config = Mock()
    board.object_selector.deselect_current_objects = Mock()

    board.on_tool_selected("Move")

    board.canvas.config.assert_called_once_with(cursor="fleur")
    board.object_selector.deselect_current_objects.assert_called_once()


def test_on_tool_selected_pen_tool(board):
    board.canvas.config = Mock()
    board.object_selector.deselect_current_objects = Mock()

    board.on_tool_selected("Pen")

    board.canvas.config.assert_called_once_with(cursor="pencil")
    board.object_selector.deselect_current_objects.assert_called_once()


def test_on_tool_selected_select_tool(board):
    board.canvas.config = Mock()
    board.object_selector.deselect_current_objects = Mock()

    board.on_tool_selected("Select")

    board.canvas.config.assert_called_once_with(cursor="hand2")
    board.object_selector.deselect_current_objects.assert_called_once()


def test_on_tool_selected_fill_tool(board):
    board.canvas.config = Mock()
    board.object_selector.deselect_current_objects = Mock()

    board.on_tool_selected("Fill")

    board.canvas.config.assert_called_once_with(cursor="plus")
    board.object_selector.deselect_current_objects.assert_called_once()


def test_on_tool_selected_text_tool(board):
    board.canvas.config = Mock()
    board.object_selector.deselect_current_objects = Mock()

    board.on_tool_selected("Text")

    board.canvas.config.assert_called_once_with(cursor="xterm")
    board.object_selector.deselect_current_objects.assert_called_once()


def test_on_tool_selected_erase_tool(board):
    board.canvas.config = Mock()
    board.canvas.bind = Mock()
    board.canvas_utils.move_eraser_frame = Mock()

    board.on_tool_selected("Erase")

    board.canvas.config.assert_called_once_with(cursor="X_cursor")
    board.canvas.bind.assert_called_once_with("<Motion>", board.canvas_utils.move_eraser_frame)


def test_on_tool_selected_polygon_tool(board):
    board.canvas.config = Mock()
    board.object_selector.deselect_current_objects = Mock()
    board.shape_handler.clear_polygon_points = Mock()

    board.on_tool_selected("Polygon")

    board.canvas.config.assert_called_once_with(cursor="")
    board.object_selector.deselect_current_objects.assert_called_once()
    board.shape_handler.clear_polygon_points.assert_not_called()


def test_destroy(board):
    board.destroy()
    assert board.canvas.winfo_exists() == 0
    assert board.x_scrollbar.winfo_exists() == 0
    assert board.y_scrollbar.winfo_exists() == 0
