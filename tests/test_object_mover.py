import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from object_mover import ObjectMover


@pytest.fixture
def object_mover():
    board = Mock()
    board.canvas = tk.Canvas()
    board.app.get_root().after = Mock()
    return ObjectMover(board)


def test_start_move(object_mover):
    event = Mock()
    event.x, event.y = 100, 100
    object_mover.object_selector.selected_objects = [1, 2]
    object_mover.canvas.tag_raise = Mock()

    object_mover.start_move(event)

    assert object_mover.canvas.tag_raise.call_count == 1
    object_mover.canvas.tag_raise.assert_any_call("selection_frame")
    assert object_mover.is_moving is True
    assert object_mover.drag_start_x == 100
    assert object_mover.drag_start_y == 100


def test_continue_move(object_mover):
    event = Mock()
    event.x, event.y = 150, 150
    object_mover.is_moving = True
    object_mover.drag_start_x, object_mover.drag_start_y = 100, 100
    object_mover.object_selector.selected_objects = [1, 2]
    object_mover.canvas.move = Mock()

    object_mover.continue_move(event)

    assert object_mover.canvas.move.call_count == 3
    object_mover.canvas.move.assert_any_call(1, 50, 50)
    object_mover.canvas.move.assert_any_call(2, 50, 50)
    object_mover.canvas.move.assert_any_call("selection_frame", 50, 50)
    assert object_mover.drag_start_x == 150
    assert object_mover.drag_start_y == 150


def test_end_move(object_mover):
    event = Mock()
    object_mover.is_moving = True
    object_mover.drag_start_x, object_mover.drag_start_y = 100, 100

    object_mover.end_move()

    assert object_mover.is_moving is False
    assert object_mover.drag_start_x is None
    assert object_mover.drag_start_y is None


def test_perform_move(object_mover):
    event = Mock()
    event.x, event.y = 150, 150
    object_mover.board.last_x, object_mover.board.last_y = 100, 100
    object_mover.object_selector.selected_objects = [1, 2]
    object_mover.canvas.move = Mock()

    object_mover.perform_move(event)

    assert object_mover.canvas.move.call_count == 3
    object_mover.canvas.move.assert_any_call(1, 50, 50)
    object_mover.canvas.move.assert_any_call(2, 50, 50)
    object_mover.canvas.move.assert_any_call("selection_frame", 50, 50)
    assert object_mover.board.last_x == 150
    assert object_mover.board.last_y == 150


@patch.object(ObjectMover, 'ensure_smooth_scroll')
def test_move_view(mock_ensure_smooth_scroll, object_mover):
    event = Mock()
    event.x, event.y = 110, 105
    object_mover.board.last_x, object_mover.board.last_y = 100, 100

    object_mover.move_view(event)

    assert object_mover.scroll_velocity_x == -1
    assert object_mover.scroll_velocity_y == -1
    assert object_mover.board.last_x == 110
    assert object_mover.board.last_y == 105
    mock_ensure_smooth_scroll.assert_called_once()


def test_smooth_scroll_when_velocity_is_greater_than_threshold(object_mover):
    object_mover.scroll_velocity_x, object_mover.scroll_velocity_y = 10, 5
    object_mover.canvas.xview_scroll = Mock()
    object_mover.canvas.yview_scroll = Mock()
    object_mover.board.app.get_root().after = Mock()

    object_mover.ensure_smooth_scroll()

    object_mover.canvas.xview_scroll.assert_called_once_with(10, "units")
    object_mover.canvas.yview_scroll.assert_called_once_with(5, "units")
    assert object_mover.scroll_velocity_x == 9
    assert object_mover.scroll_velocity_y == 4.5
    object_mover.board.app.get_root().after.assert_called_once_with(20, object_mover.smooth_scroll)
    assert object_mover.is_scrolling is True


def test_smooth_scroll_when_velocity_is_less_than_threshold(object_mover):
    object_mover.scroll_velocity_x, object_mover.scroll_velocity_y = 0.005, 0.005
    object_mover.canvas.xview_scroll = Mock()
    object_mover.canvas.yview_scroll = Mock()
    object_mover.board.app.get_root().after = Mock()

    object_mover.smooth_scroll()

    object_mover.canvas.xview_scroll.assert_not_called()
    object_mover.canvas.yview_scroll.assert_not_called()
    object_mover.board.app.get_root().after.assert_not_called()
    assert object_mover.is_scrolling is False


@patch('object_mover.ObjectMover.smooth_scroll')
def test_ensure_smooth_scroll_when_not_scrolling(smooth_scroll_mock, object_mover):
    object_mover.is_scrolling = False

    object_mover.ensure_smooth_scroll()

    assert object_mover.is_scrolling is True
    smooth_scroll_mock.assert_called_once()


@patch('object_mover.ObjectMover.smooth_scroll')
def test_ensure_smooth_scroll_when_already_scrolling(smooth_scroll_mock, object_mover):
    object_mover.is_scrolling = True

    object_mover.ensure_smooth_scroll()

    assert object_mover.is_scrolling is True
    smooth_scroll_mock.assert_not_called()
