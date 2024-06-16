import tkinter as tk
import pytest
from unittest.mock import Mock
from canvas_utils import CanvasUtils


@pytest.fixture(scope='session')
def canvas_utils():
    board = Mock()
    board.canvas = tk.Canvas()
    board.objects = []
    board.eraser_frame = None
    board.toolbox = Mock()
    board.toolbox.eraser_width = 20
    return CanvasUtils(board)


def test_erase_objects_erases_overlapping_objects(canvas_utils):
    canvas_utils.toolbox.eraser_width = 20
    canvas_utils.canvas.find_overlapping = Mock(return_value=[1, 2])
    canvas_utils.canvas.find_all = Mock(return_value=[1, 2])
    canvas_utils.canvas.gettags = Mock(return_value=[("object1",), ("object2",)])
    canvas_utils.canvas.type = Mock(side_effect=["rectangle", "oval"])
    canvas_utils.canvas.delete = Mock()
    canvas_utils.board.objects = [1, 2]

    canvas_utils.erase_objects(100, 100)

    canvas_utils.canvas.find_overlapping.assert_called_once_with(90, 90, 110, 110)
    canvas_utils.canvas.find_all.assert_called_once()
    canvas_utils.canvas.gettags.assert_called_once_with(1)
    canvas_utils.canvas.type.assert_called_once()
    canvas_utils.canvas.delete.assert_called_once()
    assert canvas_utils.board.objects == [2]


def test_erase_objects_erases_line_segments(canvas_utils):
    canvas_utils.toolbox.eraser_width = 20
    canvas_utils.canvas.find_overlapping = Mock(return_value=[1])
    canvas_utils.canvas.find_all = Mock(return_value=[1])
    canvas_utils.canvas.gettags = Mock(return_value=("object1",))
    canvas_utils.canvas.type = Mock(return_value="line")
    canvas_utils.canvas.coords = Mock(return_value=[50, 50, 150, 150])
    canvas_utils.canvas.itemcget = Mock(side_effect={
        (1, "fill"): "black",
        (1, "width"): "2",
    })
    canvas_utils.canvas.create_line = Mock()
    canvas_utils.canvas.delete = Mock()
    canvas_utils.board.objects = [1]

    canvas_utils.erase_objects(100, 100)

    canvas_utils.canvas.find_overlapping.assert_called_once_with(90, 90, 110, 110)
    canvas_utils.canvas.find_all.assert_called_once()
    canvas_utils.canvas.gettags.assert_called_once_with(1)
    canvas_utils.canvas.type.assert_called_once_with(1)
    canvas_utils.canvas.coords.assert_called_once_with(1)
    assert canvas_utils.canvas.itemcget.call_count == 2
    assert canvas_utils.canvas.create_line.call_count == 1
    canvas_utils.canvas.delete.assert_called_once_with(1)


def test_move_eraser_frame_creates_and_moves_frame(canvas_utils):
    event = Mock()
    event.x, event.y = 100, 100
    canvas_utils.toolbox.eraser_width = 20
    canvas_utils.canvas.canvasx = Mock(return_value=100)
    canvas_utils.canvas.canvasy = Mock(return_value=100)
    canvas_utils.canvas.create_rectangle = Mock(return_value=1)
    canvas_utils.canvas.coords = Mock()
    canvas_utils.board.eraser_frame = None

    canvas_utils.move_eraser_frame(event)

    canvas_utils.canvas.canvasx.assert_called_once_with(100)
    canvas_utils.canvas.canvasy.assert_called_once_with(100)
    canvas_utils.canvas.create_rectangle.assert_called_once_with(90, 90, 110, 110, outline="red", tags="eraser_frame")
    assert canvas_utils.board.eraser_frame == 1


def test_move_eraser_frame_moves_existing_frame(canvas_utils):
    event = Mock()
    event.x, event.y = 100, 100
    canvas_utils.toolbox.eraser_width = 20
    canvas_utils.canvas.canvasx = Mock(return_value=100)
    canvas_utils.canvas.canvasy = Mock(return_value=100)
    canvas_utils.canvas.coords = Mock()
    canvas_utils.board.eraser_frame = 1

    canvas_utils.move_eraser_frame(event)

    canvas_utils.canvas.canvasx.assert_called_once_with(100)
    canvas_utils.canvas.canvasy.assert_called_once_with(100)
    canvas_utils.canvas.coords.assert_called_once_with(1, 90, 90, 110, 110)


def test_return_to_middle(canvas_utils):
    canvas_utils.canvas.xview_moveto = Mock()
    canvas_utils.canvas.yview_moveto = Mock()

    canvas_utils.return_to_middle()

    canvas_utils.canvas.xview_moveto.assert_called_once_with(0.5)
    canvas_utils.canvas.yview_moveto.assert_called_once_with(0.5)
