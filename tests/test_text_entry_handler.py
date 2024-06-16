import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from text_entry_handler import TextEntryHandler


@pytest.fixture
def text_entry_handler():
    board = Mock()
    board.canvas = Mock(spec=tk.Canvas)
    board.objects = []
    board.text_entry = None
    board.toolbox = Mock()
    return TextEntryHandler(board)


def test_create_text_entry(text_entry_handler):
    event = Mock()
    event.x, event.y = 100, 100
    text_entry_handler.toolbox.text_font_name = "Arial"
    text_entry_handler.toolbox.text_font_size = 12
    text_entry_handler.toolbox.text_color = "black"
    text_entry_handler.loaded_fonts = {("Arial", 12): Mock(name="Arial", size=12)}
    text_entry_handler.canvas.canvasx = Mock(return_value=100)
    text_entry_handler.canvas.canvasy = Mock(return_value=100)
    text_entry_handler.canvas.create_text = Mock(return_value=1)
    text_entry_handler.create_text_box = Mock()
    text_entry_handler.board.objects = []

    text_entry_handler.create_text_entry(event)

    text_entry_handler.canvas.canvasx.assert_called_once_with(100)
    text_entry_handler.canvas.canvasy.assert_called_once_with(100)
    text_entry_handler.canvas.create_text.assert_called_once()
    call_args, call_kwargs = text_entry_handler.canvas.create_text.call_args
    assert call_args == (100, 100)
    assert call_kwargs['text'] == ""
    assert call_kwargs['font'][1] == 12
    assert call_kwargs['fill'] == "black"
    assert call_kwargs['tags'] == ("object0",)
    text_entry_handler.create_text_box.assert_called_once_with(event, 1)


@patch('text_entry_handler.tk.Label')
@patch('text_entry_handler.tk.Text')
def test_create_text_box(text_mock, label_mock, text_entry_handler):
    event = Mock()
    event.x, event.y = 100, 100
    text_object = 1
    text_entry_handler.canvas.canvasx = Mock(return_value=100)
    text_entry_handler.canvas.canvasy = Mock(return_value=100)
    text_entry_handler.canvas.create_window = Mock(side_effect=[2, 3])
    text_instance = text_mock.return_value
    text_instance.bind = Mock()

    text_entry_handler.create_text_box(event, text_object)

    label_mock.assert_called_once_with(text_entry_handler.canvas,
                                       text="Press 'Enter' to confirm\nPress 'Esc' to cancel")
    text_entry_handler.canvas.create_window.assert_any_call(100, 90, window=label_mock.return_value, anchor=tk.S)
    text_mock.assert_called_once_with(text_entry_handler.canvas, height=1, width=20)
    text_entry_handler.canvas.create_window.assert_any_call(100, 100, window=text_instance, anchor=tk.N)
    text_instance.insert.assert_called_once_with("1.0", "Enter text here...")
    text_instance.focus_set.assert_called_once()
    assert text_instance.bind.call_count == 4


def test_cancel_text_entry(text_entry_handler):
    text_box = Mock()
    text_object = 1
    label_window = 2
    text_box_window = 3
    text_entry_handler.canvas.delete = Mock()

    text_entry_handler.cancel_text_entry(text_box, text_object, label_window, text_box_window)

    text_entry_handler.canvas.delete.assert_any_call(text_object)
    text_entry_handler.canvas.delete.assert_any_call(label_window)
    text_entry_handler.canvas.delete.assert_any_call(text_box_window)
    text_box.destroy.assert_called_once()


def test_edit_text_entry(text_entry_handler):
    text_entry_handler.board.text_entry = 1
    text_entry_handler.canvas.itemconfigure = Mock()

    text_entry_handler.edit_text_entry(None)

    text_entry_handler.canvas.itemconfigure.assert_called_once_with(1, state="hidden")


def test_update_text_entry_with_new_text(text_entry_handler):
    text_box = Mock()
    text_box.get = Mock(return_value="New Text")
    text_object = 1
    label_window = 2
    text_box_window = 3
    text_entry_handler.toolbox.text_font_name = "Arial"
    text_entry_handler.toolbox.text_font_size = 12
    text_entry_handler.toolbox.text_color = "black"
    text_entry_handler.loaded_fonts = {("Arial", 12): Mock(name="Arial", size=12)}
    text_entry_handler.canvas.itemconfigure = Mock()
    text_entry_handler.canvas.delete = Mock()

    text_entry_handler.update_text_entry(text_box, text_object, label_window, text_box_window)

    text_box.get.assert_called_once_with("1.0", tk.END)
    assert text_entry_handler.canvas.itemconfigure.call_count == 2
    call_args_list = text_entry_handler.canvas.itemconfigure.call_args_list
    assert call_args_list[0][0][0] == text_object
    assert call_args_list[0][1]['text'] == "New Text"
    assert call_args_list[0][1]['font'][1] == 12
    assert call_args_list[0][1]['fill'] == "black"
    assert call_args_list[1][0][0] == text_object
    assert call_args_list[1][1]['state'] == "normal"
    text_entry_handler.canvas.delete.assert_any_call(label_window)
    text_entry_handler.canvas.delete.assert_any_call(text_box_window)
    text_box.destroy.assert_called_once()


def test_update_text_entry_with_empty_text(text_entry_handler):
    text_box = Mock()
    text_box.get = Mock(return_value="\n")
    text_object = 1
    label_window = 2
    text_box_window = 3
    text_entry_handler.canvas.delete = Mock()

    text_entry_handler.update_text_entry(text_box, text_object, label_window, text_box_window)

    text_box.get.assert_called_once_with("1.0", tk.END)
    text_entry_handler.canvas.delete.assert_any_call(text_object)
    text_entry_handler.canvas.delete.assert_any_call(label_window)
    text_entry_handler.canvas.delete.assert_any_call(text_box_window)
    text_box.destroy.assert_called_once()
