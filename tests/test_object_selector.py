import tkinter as tk
import pytest
from unittest.mock import Mock
from object_selector import ObjectSelector


@pytest.fixture
def object_selector():
    board = Mock()
    board.canvas = tk.Canvas()
    return ObjectSelector(board)


def test_handle_select_tool_click_when_object_is_clicked(object_selector):
    event = Mock()
    event.x, event.y = 100, 100
    object_selector.canvas.find_withtag = Mock(return_value=[1])
    object_selector.select_object = Mock()

    object_selector.handle_select_tool_click(event)

    object_selector.canvas.find_withtag.assert_called_once_with(tk.CURRENT)
    object_selector.select_object.assert_called_once_with(1)


def test_handle_select_tool_click_when_no_object_is_clicked(object_selector):
    event = Mock()
    event.x, event.y = 100, 100
    object_selector.canvas.find_withtag = Mock(return_value=[])
    object_selector.deselect_current_objects = Mock()

    object_selector.handle_select_tool_click(event)

    object_selector.canvas.find_withtag.assert_called_once_with(tk.CURRENT)
    object_selector.deselect_current_objects.assert_called_once()
    assert object_selector.selection_start_x == 100
    assert object_selector.selection_start_y == 100
    assert object_selector.is_dragging is True


def test_handle_select_tool_drag(object_selector):
    event = Mock()
    event.x, event.y = 150, 150
    object_selector.is_dragging = True
    object_selector.selection_frame = 1
    object_selector.selection_start_x, object_selector.selection_start_y = 100, 100
    object_selector.canvas.coords = Mock()

    object_selector.handle_select_tool_drag(event)

    object_selector.canvas.coords.assert_called_once_with(1, 100, 100, 150, 150)


def test_handle_select_tool_release_when_objects_are_selected(object_selector):
    object_selector.is_dragging = True
    object_selector.selection_frame = 1
    object_selector.canvas.coords = Mock(return_value=[50, 50, 150, 150])
    object_selector.canvas.find_enclosed = Mock(return_value=[1, 2, 3])
    object_selector.select_multiple_objects = Mock()

    object_selector.handle_select_tool_release(None)

    object_selector.canvas.coords.assert_called_once_with(1)
    object_selector.canvas.find_enclosed.assert_called_once_with(50, 50, 150, 150)
    object_selector.select_multiple_objects.assert_called_once_with([1, 2, 3])
    assert object_selector.selection_start_x == 0
    assert object_selector.selection_start_y == 0
    assert object_selector.is_dragging is False


def test_handle_select_tool_release_when_no_objects_are_selected(object_selector):
    object_selector.is_dragging = True
    object_selector.selection_frame = 1
    object_selector.canvas.coords = Mock(return_value=[50, 50, 150, 150])
    object_selector.canvas.find_enclosed = Mock(return_value=[])
    object_selector.deselect_current_objects = Mock()

    object_selector.handle_select_tool_release(None)

    object_selector.canvas.coords.assert_called_once_with(1)
    object_selector.canvas.find_enclosed.assert_called_once_with(50, 50, 150, 150)
    object_selector.deselect_current_objects.assert_called_once()
    assert object_selector.selection_start_x == 0
    assert object_selector.selection_start_y == 0
    assert object_selector.is_dragging is False


def test_select_object(object_selector):
    object_selector.selected_objects = []
    object_selector.deselect_current_objects = Mock()
    object_selector.draw_selection_frame = Mock()

    object_selector.select_object(1)

    object_selector.deselect_current_objects.assert_called_once()
    assert object_selector.selected_objects == [1]
    object_selector.draw_selection_frame.assert_called_once()


def test_select_object_when_already_selected(object_selector):
    object_selector.selected_objects = [1]
    object_selector.draw_selection_frame = Mock()
    object_selector.select_object(1)
    assert object_selector.selected_objects == []
    object_selector.draw_selection_frame.assert_not_called()


def test_select_multiple_objects(object_selector):
    objects = [1, 2, 3]
    object_selector.draw_selection_frame = Mock()

    object_selector.select_multiple_objects(objects)

    assert object_selector.selected_objects == objects
    object_selector.draw_selection_frame.assert_called_once()


def test_deselect_current_objects(object_selector):
    object_selector.selected_objects = [1, 2, 3]
    object_selector.canvas.delete = Mock()
    object_selector.selection_frame = 1

    object_selector.deselect_current_objects()

    assert object_selector.selected_objects == []
    object_selector.canvas.delete.assert_called_once_with("selection_frame")
    assert object_selector.selection_frame is None


def test_draw_selection_frame(object_selector):
    object_selector.canvas.delete = Mock()
    object_selector.selected_objects = [1, 2]
    object_selector.canvas.bbox = Mock(return_value=(50, 50, 150, 150))
    object_selector.canvas.create_rectangle = Mock(return_value=1)
    object_selector.selection_frame_padding = 10  # Set the attribute directly

    object_selector.draw_selection_frame()

    object_selector.canvas.delete.assert_called_once_with("selection_frame")
    object_selector.canvas.bbox.assert_called_once_with(1, 2)
    object_selector.canvas.create_rectangle.assert_called_once_with(40, 40, 160, 160, outline="black", dash=(4, 2),
                                                                    tags="selection_frame")
    assert object_selector.selection_frame == 1


def test_draw_selection_frame_when_bbox_returns_none(object_selector):
    object_selector.canvas.delete = Mock()
    object_selector.selected_objects = [1, 2]
    object_selector.canvas.bbox = Mock(return_value=None)
    object_selector.canvas.create_rectangle = Mock()

    object_selector.draw_selection_frame()

    object_selector.canvas.delete.assert_called_once_with("selection_frame")
    object_selector.canvas.bbox.assert_called_once_with(1, 2)
    object_selector.canvas.create_rectangle.assert_not_called()
    assert object_selector.selection_frame is None


def test_is_click_inside_selection_frame_when_inside(object_selector):
    event = Mock()
    event.x, event.y = 100, 100
    object_selector.selection_frame = 1
    object_selector.canvas.coords = Mock(return_value=[50, 50, 150, 150])

    result = object_selector.is_click_inside_selection_frame(event)

    assert result is True


def test_is_click_inside_selection_frame_when_outside(object_selector):
    event = Mock()
    event.x, event.y = 200, 200
    object_selector.selection_frame = 1
    object_selector.canvas.coords = Mock(return_value=[50, 50, 150, 150])

    result = object_selector.is_click_inside_selection_frame(event)

    assert result is False
