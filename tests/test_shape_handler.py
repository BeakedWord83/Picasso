import tkinter as tk
from unittest.mock import Mock, call

import pytest

from shape_handler import ShapeHandler


@pytest.fixture
def shape_handler():
    board = Mock()
    board.canvas = tk.Canvas()
    board.last_x, board.last_y = 100, 100
    board.objects = []
    return ShapeHandler(board)


def test_start_shape_for_rectangle(shape_handler):
    shape_handler.toolbox.current_tool = "Rectangle"
    shape_handler.canvas.create_rectangle = Mock(return_value=1)

    shape_handler.start_shape()

    shape_handler.canvas.create_rectangle.assert_called_once_with(100, 100, 100, 100, width=5)
    assert shape_handler.temp_shape == 1


def test_start_shape_for_circle(shape_handler):
    shape_handler.toolbox.current_tool = "Circle"
    shape_handler.canvas.create_oval = Mock(return_value=1)

    shape_handler.start_shape()

    shape_handler.canvas.create_oval.assert_called_once_with(100, 100, 100, 100, width=5)
    assert shape_handler.temp_shape == 1


def test_start_shape_for_triangle(shape_handler):
    shape_handler.toolbox.current_tool = "Triangle"
    shape_handler.canvas.create_polygon = Mock(return_value=1)

    shape_handler.start_shape()

    shape_handler.canvas.create_polygon.assert_called_once_with(100, 100, 100, 100, 100, 100, width=5)
    assert shape_handler.temp_shape == 1


def test_start_shape_for_line(shape_handler):
    shape_handler.toolbox.current_tool = "Line"
    shape_handler.canvas.create_line = Mock(return_value=1)

    shape_handler.start_shape()

    shape_handler.canvas.create_line.assert_called_once_with(100, 100, 100, 100, width=5)
    assert shape_handler.temp_shape == 1


def test_start_shape_for_polygon(shape_handler):
    shape_handler.toolbox.current_tool = "Polygon"

    shape_handler.start_shape()

    assert shape_handler.polygon_points == [(100, 100)]


def test_update_shape_for_rectangle(shape_handler):
    event = Mock()
    event.x, event.y = 200, 150
    shape_handler.toolbox.current_tool = "Rectangle"
    shape_handler.temp_shape = 1
    shape_handler.canvas.coords = Mock()

    shape_handler.update_shape(event)

    shape_handler.canvas.coords.assert_called_once_with(1, 100, 100, 200, 150)


def test_update_shape_for_circle(shape_handler):
    event = Mock()
    event.x, event.y = 200, 150
    shape_handler.toolbox.current_tool = "Circle"
    shape_handler.temp_shape = 1
    shape_handler.canvas.coords = Mock()

    shape_handler.update_shape(event)

    x1, y1 = 100, 100
    x2, y2 = 200, 150
    radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    shape_handler.canvas.coords.assert_called_once_with(1, cx - radius, cy - radius, cx + radius, cy + radius)


def test_update_shape_for_triangle(shape_handler):
    event = Mock()
    event.x, event.y = 200, 150
    shape_handler.toolbox.current_tool = "Triangle"
    shape_handler.temp_shape = 1
    shape_handler.canvas.coords = Mock()

    shape_handler.update_shape(event)

    x1, y1 = 100, 100
    x2, y2 = 200, 150
    dx, dy = x2 - x1, y2 - y1
    side = (dx ** 2 + dy ** 2) ** 0.5
    if side != 0:
        h = side * (3 ** 0.5) / 2
        x3 = x1 + dx / 2
        y3 = y1 + (y2 - y1) / 2 + h * dx / side
        shape_handler.canvas.coords.assert_called_once_with(1, x1, y1, x2, y2, x3, y3)


def test_draw_pen(shape_handler):
    shape_handler.board.drawing = True
    shape_handler.toolbox.current_tool = "Pen"
    shape_handler.toolbox.pen_color = "black"
    shape_handler.toolbox.pen_width = 2
    shape_handler.canvas.create_line = Mock(side_effect=[1, 2])  # Return different values for each call

    shape_handler.draw_pen(150, 200)
    shape_handler.draw_pen(160, 210)

    assert shape_handler.current_object_tag == "object0"
    assert shape_handler.pen_points == [(150, 200), (160, 210)]

    # Assert that create_line was called twice with the expected arguments
    expected_calls = [
        call(150, 200, 150, 200, fill="black", width=2, tags="object0"),
        call((150, 200), (160, 210), fill="black", width=2, tags="object0")
    ]
    shape_handler.canvas.create_line.assert_has_calls(expected_calls)

    assert shape_handler.current_object == 2
    assert shape_handler.board.last_x == 160
    assert shape_handler.board.last_y == 210


def test_finalize_shape_for_rectangle(shape_handler):
    shape_handler.toolbox.current_tool = "Rectangle"
    shape_handler.toolbox.pen_color = "black"
    shape_handler.toolbox.pen_width = 2
    shape_handler.temp_shape = 1
    shape_handler.canvas.coords = Mock(return_value=[100, 100, 200, 150])
    shape_handler.canvas.create_rectangle = Mock(return_value=2)
    shape_handler.canvas.delete = Mock()
    shape_handler.board.objects = []  # Add this line to initialize board.objects as an empty list

    shape_handler.finalize_shape()

    shape_handler.canvas.coords.assert_called_once_with(1)
    shape_handler.canvas.create_rectangle.assert_called_once_with(100, 100, 200, 150, fill="black", width=2)
    shape_handler.canvas.delete.assert_called_once_with(1)
    assert shape_handler.current_object_tag == "object0"
    assert shape_handler.current_object == 2


def test_draw_polygon_point(shape_handler):
    shape_handler.canvas.create_oval = Mock(return_value=1)
    shape_handler.update_polygon_preview = Mock()

    shape_handler.draw_polygon_point(100, 100)

    shape_handler.canvas.create_oval.assert_called_once_with(94, 94, 106, 106, fill="green", outline="black", width=2,
                                                             tags=("polygon_point",))
    assert shape_handler.polygon_temp_shapes == [1]
    shape_handler.update_polygon_preview.assert_called_once()
    assert shape_handler.polygon_points == [(100, 100)]


def test_handle_polygon_hover(shape_handler):
    event = Mock()
    event.x, event.y = 105, 105
    shape_handler.toolbox.current_tool = "Polygon"
    shape_handler.polygon_temp_shapes = [1]
    shape_handler.canvas.coords = Mock(side_effect=[[100, 100, 110, 110], [95, 95, 115, 115]])

    shape_handler.handle_polygon_hover(event)

    assert shape_handler.canvas.coords.call_count == 2
    shape_handler.canvas.coords.assert_any_call(1, 95, 95, 115, 115)


def test_finalize_polygon(shape_handler):
    shape_handler.polygon_points = [(100, 100), (200, 150), (150, 200)]
    shape_handler.toolbox.pen_color = "black"
    shape_handler.toolbox.pen_width = 2
    shape_handler.canvas.create_polygon = Mock(return_value=1)
    shape_handler.clear_polygon_points = Mock()
    shape_handler.board.objects = []  # Add this line to initialize board.objects as an empty list

    shape_handler.finalize_polygon()

    shape_handler.canvas.create_polygon.assert_called_once_with([(100, 100), (200, 150), (150, 200)], fill="black",
                                                                width=2, tags="object0")
    assert shape_handler.current_object_tag == "object0"
    assert shape_handler.current_object == 1
    shape_handler.clear_polygon_points.assert_called_once()


def test_handle_polygon_click(shape_handler):
    event = Mock()
    event.x, event.y = 200, 200
    shape_handler.toolbox.current_tool = "Polygon"
    shape_handler.polygon_points = [(100, 100)]

    shape_handler.handle_polygon_click(event)

    assert shape_handler.polygon_points == [(100, 100), (200, 200)]


def test_handle_polygon_click_finalize_polygon(shape_handler):
    event = Mock()
    event.x, event.y = 101, 101  # Near the starting point (100, 100)
    shape_handler.toolbox.current_tool = "Polygon"
    shape_handler.polygon_points = [(100, 100), (200, 200), (150, 250)]
    shape_handler.finalize_polygon = Mock()

    shape_handler.handle_polygon_click(event)

    shape_handler.finalize_polygon.assert_called_once()


def test_handle_polygon_click_near_existing_point(shape_handler):
    event = Mock()
    event.x, event.y = 199, 199  # Near the point (200, 200)
    shape_handler.toolbox.current_tool = "Polygon"
    shape_handler.polygon_points = [(100, 100), (200, 200), (150, 250)]
    shape_handler.draw_polygon_point = Mock()

    shape_handler.handle_polygon_click(event)

    shape_handler.draw_polygon_point.assert_not_called()


def test_handle_polygon_click_different_tool(shape_handler):
    event = Mock()
    event.x, event.y = 300, 300
    shape_handler.toolbox.current_tool = "Rectangle"  # Different tool selected
    shape_handler.polygon_points = [(100, 100), (200, 200), (150, 250)]
    shape_handler.draw_polygon_point = Mock()

    shape_handler.handle_polygon_click(event)

    shape_handler.draw_polygon_point.assert_not_called()
    assert shape_handler.polygon_points == [(100, 100), (200, 200), (150, 250)]
