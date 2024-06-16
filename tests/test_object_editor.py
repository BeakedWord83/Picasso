import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from object_editor import ObjectEditor


@pytest.fixture(scope="session")
def object_editor():
    board = Mock()
    board.canvas = tk.Canvas()
    return ObjectEditor(board)


def test_copy_selected_object(object_editor):
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.coords = Mock(return_value=[10, 10, 20, 20])
    object_editor.canvas.type = Mock(return_value="rectangle")
    object_editor.canvas.itemcget = Mock(side_effect=["red", "2", "blue", "Text", "Arial"])

    object_editor.copy_selected_object()

    assert object_editor.copied_object == {
        'coords': [10, 10, 20, 20],
        'type': 'rectangle',
        'fill': 'red',
        'outline': 'blue',
        'width': '2',
        'text': None,
        'font': None
    }


def test_paste_object_at_position_for_line(object_editor):
    object_editor.board.right_click_x, object_editor.board.right_click_y = 100, 100
    object_editor.copied_object = {
        'coords': [10, 10, 20, 20],
        'type': 'line',
        'fill': 'red',
        'outline': None,
        'width': '2',
        'text': None,
        'font': None
    }
    object_editor.canvas.create_line = Mock(return_value=1)
    object_editor.board.objects = []  # Initialize board.objects as an empty list

    object_editor.paste_object_at_position()

    # Calculate the expected coordinates for the pasted line
    x1, y1, x2, y2 = 10, 10, 20, 20
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    dx = 100 - center_x
    dy = 100 - center_y
    expected_x1 = x1 + dx
    expected_y1 = y1 + dy
    expected_x2 = x2 + dx
    expected_y2 = y2 + dy

    object_editor.canvas.create_line.assert_called_once_with(expected_x1, expected_y1, expected_x2, expected_y2,
                                                             fill='red', width='2', tags=('object0',))
    assert object_editor.board.objects == [1]


def test_paste_object_at_position_for_text(object_editor):
    object_editor.board.right_click_x, object_editor.board.right_click_y = 100, 100
    object_editor.copied_object = {
        'coords': [10, 10],
        'type': 'text',
        'fill': 'red',
        'outline': None,
        'width': '2',
        'text': 'Hello',
        'font': 'Arial'
    }
    object_editor.canvas.create_text = Mock(return_value=1)
    object_editor.board.objects = []  # Initialize board.objects as an empty list

    object_editor.paste_object_at_position()

    object_editor.canvas.create_text.assert_called_once_with(100, 100, text='Hello', font='Arial', fill='red',
                                                             tags=('object0',))
    assert object_editor.board.objects == [1]


def test_paste_object_at_position_for_polygon(object_editor):
    object_editor.board.right_click_x, object_editor.board.right_click_y = 100, 100
    object_editor.copied_object = {
        'coords': [10, 10, 20, 20, 30, 30],
        'type': 'polygon',
        'fill': 'red',
        'outline': 'blue',
        'width': '2',
        'text': None,
        'font': None
    }
    object_editor.canvas.create_polygon = Mock(return_value=1)
    object_editor.board.objects = []  # Initialize board.objects as an empty list

    object_editor.paste_object_at_position()

    object_editor.canvas.create_polygon.assert_called_once_with(90, 90, 100, 100, 110, 110, fill='red', outline='blue',
                                                                width='2', tags=('object0',))
    assert object_editor.board.objects == [1]


def test_paste_object_at_position_for_rectangle(object_editor):
    object_editor.board.right_click_x, object_editor.board.right_click_y = 100, 100
    object_editor.copied_object = {
        'coords': [10, 10, 20, 20],
        'type': 'rectangle',
        'fill': 'red',
        'outline': 'blue',
        'width': '2',
        'text': None,
        'font': None
    }
    object_editor.canvas.create_rectangle = Mock(return_value=1)
    object_editor.board.objects = []  # Initialize board.objects as an empty list

    object_editor.paste_object_at_position()

    object_editor.canvas.create_rectangle.assert_called_once_with(95, 95, 105, 105, fill='red', outline='blue',
                                                                   width='2', tags=('object0',))
    assert object_editor.board.objects == [1]


def test_delete_selected_object(object_editor):
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.delete = Mock()
    object_editor.board.objects = [1]

    object_editor.delete_selected_object()

    object_editor.canvas.delete.assert_any_call(1)
    object_editor.canvas.delete.assert_any_call("selection_frame")
    assert object_editor.board.objects == []
    assert object_editor.object_selector.selected_objects == []
    assert object_editor.object_selector.selection_frame is None


@patch('object_editor.colorchooser.askcolor', return_value=("", "#FF0000"))
def test_change_selected_object_color_for_line(askcolor_mock, object_editor):
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.type = Mock(return_value="line")
    object_editor.canvas.itemconfig = Mock()

    object_editor.change_selected_object_color()

    object_editor.canvas.itemconfig.assert_called_once_with(1, fill="#FF0000")


@patch('object_editor.colorchooser.askcolor', return_value=("", "#FF0000"))
def test_change_selected_object_color_for_rectangle(askcolor_mock, object_editor):
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.type = Mock(return_value="rectangle")
    object_editor.canvas.itemconfig = Mock()

    object_editor.change_selected_object_color()

    object_editor.canvas.itemconfig.assert_called_once_with(1, fill="#FF0000", outline="#FF0000")


@patch('object_editor.WidthDialog')
def test_change_selected_object_width(width_dialog_mock, object_editor):
    width_dialog_instance = width_dialog_mock.return_value
    width_dialog_instance.result = 5
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.itemcget = Mock(return_value="2")
    object_editor.canvas.itemconfig = Mock()
    object_editor.board.app.get_root().wait_window = Mock()

    object_editor.change_selected_object_width()

    width_dialog_mock.assert_called_once_with(object_editor.board.app.get_root(), '2')
    object_editor.board.app.get_root().wait_window.assert_called_once_with(width_dialog_instance)
    object_editor.canvas.itemconfig.assert_called_once_with(1, width=5)


@patch('object_editor.FontDialog')
def test_change_selected_object_font(font_dialog_mock, object_editor):
    font_dialog_instance = font_dialog_mock.return_value
    font_dialog_instance.result = "Arial"
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.type = Mock(return_value="text")
    object_editor.canvas.itemcget = Mock(return_value="Helvetica 12")
    object_editor.canvas.itemconfig = Mock()
    object_editor.board.app.get_root().wait_window = Mock()

    object_editor.change_selected_object_font()

    object_editor.canvas.itemcget.assert_called_once_with(1, "font")
    font_dialog_mock.assert_called_once_with(object_editor.board.app.get_root(), "Helvetica")
    object_editor.board.app.get_root().wait_window.assert_called_once_with(font_dialog_instance)
    object_editor.canvas.itemconfig.assert_called_once_with(1, font=("Arial", "12"))


@patch('object_editor.FontSizeDialog')
def test_change_selected_object_font_size(font_size_dialog_mock, object_editor):
    font_size_dialog_instance = font_size_dialog_mock.return_value
    font_size_dialog_instance.result = "16"
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.type = Mock(return_value="text")
    object_editor.canvas.itemcget = Mock(return_value="Helvetica 12")
    object_editor.canvas.itemconfig = Mock()
    object_editor.board.app.get_root().wait_window = Mock()
    object_editor.object_selector.draw_selection_frame = Mock()

    object_editor.change_selected_object_font_size()

    object_editor.canvas.itemcget.assert_called_once_with(1, "font")
    font_size_dialog_mock.assert_called_once_with(object_editor.board.app.get_root(), "12")
    object_editor.board.app.get_root().wait_window.assert_called_once_with(font_size_dialog_instance)
    object_editor.canvas.itemconfig.assert_called_once_with(1, font=("Helvetica", "16"))
    object_editor.object_selector.draw_selection_frame.assert_called_once()


def test_move_selected_object_to_front(object_editor):
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.tag_raise = Mock()

    object_editor.move_selected_object_to_front()

    object_editor.canvas.tag_raise.assert_called_once_with(1)


def test_move_selected_object_to_back(object_editor):
    object_editor.object_selector.selected_objects = [1]
    object_editor.canvas.tag_lower = Mock()

    object_editor.move_selected_object_to_back()

    object_editor.canvas.tag_lower.assert_called_once_with(1)
