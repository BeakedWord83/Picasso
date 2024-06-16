import pytest
import tkinter as tk
from unittest.mock import Mock, patch

from fill_handler import FillHandler


@pytest.fixture(scope='session')
def root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def fill_handler(root):
    board = Mock()
    board.canvas = tk.Canvas(root)
    board.canvas.itemconfig = Mock()
    board.toolbox = Mock()
    fill_handler = FillHandler(board)
    return fill_handler


@patch('tkinter.Canvas.find_overlapping')
def test_fill_area_text(mock_find_overlapping, fill_handler):
    event = Mock()
    event.x = 100
    event.y = 100
    mock_find_overlapping.return_value = [1]
    fill_handler.canvas.type = Mock(return_value="text")
    fill_handler.toolbox.fill_color = "red"

    fill_handler.fill_area(event)

    fill_handler.canvas.itemconfig.assert_called_once_with(1, fill="red")


@patch('tkinter.Canvas.find_overlapping')
def test_fill_area_line(mock_find_overlapping, fill_handler):
    event = Mock()
    event.x = 100
    event.y = 100
    mock_find_overlapping.return_value = [1]
    fill_handler.canvas.type = Mock(return_value="line")
    fill_handler.toolbox.fill_color = "blue"

    fill_handler.fill_area(event)

    fill_handler.canvas.itemconfig.assert_called_once_with(1, fill="blue")


@patch('tkinter.Canvas.find_overlapping')
def test_fill_area_rectangle(mock_find_overlapping, fill_handler):
    event = Mock()
    event.x = 100
    event.y = 100
    mock_find_overlapping.return_value = [1]
    fill_handler.canvas.type = Mock(return_value="rectangle")
    fill_handler.toolbox.fill_color = "green"

    fill_handler.fill_area(event)

    fill_handler.canvas.itemconfig.assert_called_once_with(1, fill="green", outline="green")


@patch('tkinter.Canvas.find_overlapping')
def test_fill_area_oval(mock_find_overlapping, fill_handler):
    event = Mock()
    event.x = 100
    event.y = 100
    mock_find_overlapping.return_value = [1]
    fill_handler.canvas.type = Mock(return_value="oval")
    fill_handler.toolbox.fill_color = "orange"

    fill_handler.fill_area(event)

    fill_handler.canvas.itemconfig.assert_called_once_with(1, fill="orange", outline="orange")


@patch('tkinter.Canvas.find_overlapping')
def test_fill_area_polygon(mock_find_overlapping, fill_handler):
    event = Mock()
    event.x = 100
    event.y = 100
    mock_find_overlapping.return_value = [1]
    fill_handler.canvas.type = Mock(return_value="polygon")
    fill_handler.toolbox.fill_color = "purple"

    fill_handler.fill_area(event)

    fill_handler.canvas.itemconfig.assert_called_once_with(1, fill="purple")


@patch('tkinter.Canvas.find_overlapping')
def test_fill_area_no_items(mock_find_overlapping, fill_handler):
    event = Mock()
    event.x = 100
    event.y = 100
    mock_find_overlapping.return_value = []

    fill_handler.fill_area(event)

    fill_handler.canvas.itemconfig.assert_not_called()
