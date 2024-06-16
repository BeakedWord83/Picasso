import json
import tkinter as tk

import pyglet
import pytest

from unittest.mock import Mock, patch, call
from file_handler import FileHandler


@pytest.fixture
def file_handler():
    board = Mock()
    board.canvas = Mock(spec=tk.Canvas)
    board.loaded_fonts = {}
    return FileHandler(board)


def test_new_board(file_handler):
    file_handler.canvas.delete = Mock()
    file_handler.board.canvas_utils.return_to_middle = Mock()

    file_handler.new_board()

    file_handler.canvas.delete.assert_called_once_with("all")
    assert file_handler.board.objects == []
    assert file_handler.board.drawing is False
    file_handler.board.canvas_utils.return_to_middle.assert_called_once()


@patch('file_handler.filedialog.asksaveasfilename', return_value="test.pcso")
def test_save_board_dialog(asksaveasfilename_mock, file_handler):
    file_handler.save_board = Mock()

    file_handler.save_board_dialog()

    asksaveasfilename_mock.assert_called_once_with(initialdir="./boards", defaultextension=".pcso",
                                                   filetypes=[("Picasso Board", "*.pcso")])
    file_handler.save_board.assert_called_once_with("test.pcso")


@patch('file_handler.tk.filedialog.askopenfilename', return_value="test.pcso")
def test_open_board_dialog(askopenfilename_mock, file_handler):
    file_handler.load_board = Mock()

    file_handler.open_board_dialog()

    askopenfilename_mock.assert_called_once_with(initialdir="./boards", filetypes=[("Picasso Board", "*.pcso")],
                                                 defaultextension=".pcso")
    file_handler.load_board.assert_called_once_with("test.pcso")


def test_save_board(file_handler, tmp_path):
    file_handler.canvas.type = Mock(side_effect=["rectangle", "text"])
    file_handler.canvas.coords = Mock(side_effect=[[10, 10, 20, 20], [30, 30]])
    itemcget_side_effects = [
        ["red", "2", "blue"],  # Side effects for the rectangle object
        ["red", "2", "Arial 12", "Hello"]  # Side effects for the text object
    ]
    file_handler.canvas.itemcget = Mock(side_effect=lambda obj, attr: itemcget_side_effects[obj - 1].pop(0))
    file_handler.canvas.find_all = Mock(return_value=[1, 2])
    file_handler.board.objects = [1, 2]

    file_path = tmp_path / "test.pcso"
    file_handler.save_board(str(file_path))

    with open(file_path, 'r') as f:
        board_state = json.load(f)

    assert board_state == {
        'objects': [
            {'type': 'rectangle', 'coords': [10, 10, 20, 20], 'fill': 'red', 'width': '2', 'z-index': 0,
             'outline': 'blue'},
            {'type': 'text', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 1, 'font': 'Arial 12',
             'text': 'Hello'}
        ]
    }


def test_load_objects(file_handler):
    objects_state = [
        {'type': 'rectangle', 'coords': [10, 10, 20, 20], 'fill': 'red', 'width': '2', 'z-index': 1, 'outline': 'blue'},
        {'type': 'text', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 0, 'font': 'Arial 12',
         'text': 'Hello'}
    ]
    file_handler.board.objects = []
    file_handler.canvas.create_rectangle = Mock(return_value=1)
    file_handler.canvas.create_text = Mock(return_value=2)
    font_name = 'Arial'
    size = 12
    pyglet_font = pyglet.font.load(font_name, size)
    file_handler.loaded_fonts = {('Arial', 12): pyglet_font}

    file_handler.load_objects(objects_state)

    assert file_handler.canvas.create_rectangle.call_args_list == [
        call(10, 10, 20, 20, fill='red', outline='blue', width='2'),
    ]
    assert file_handler.canvas.create_text.call_args_list == [
        call(30, 30, text='Hello', font=('Arial', 12), fill='red'),
    ]

    assert file_handler.board.objects == [1, 2]


@patch('file_handler.FileHandler.new_board')
@patch('file_handler.FileHandler.load_objects')
def test_load_board(load_objects_mock, new_board_mock, file_handler, tmp_path):
    board_state = {
        'objects': [
            {'type': 'rectangle', 'coords': [10, 10, 20, 20], 'fill': 'red', 'width': '2', 'z-index': 0,
             'outline': 'blue'},
            {'type': 'text', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 1, 'font': 'Arial 12',
             'text': 'Hello'}
        ]
    }
    file_path = tmp_path / "test.pcso"
    with open(file_path, 'w') as f:
        json.dump(board_state, f)

    file_handler.load_board(str(file_path))

    new_board_mock.assert_called_once()
    load_objects_mock.assert_called_once_with(board_state['objects'])


@patch('file_handler.filedialog.asksaveasfilename', return_value="")
def test_save_board_dialog_cancel(asksaveasfilename_mock, file_handler):
    file_handler.save_board = Mock()

    file_handler.save_board_dialog()

    asksaveasfilename_mock.assert_called_once_with(initialdir="./boards", defaultextension=".pcso",
                                                   filetypes=[("Picasso Board", "*.pcso")])
    file_handler.save_board.assert_not_called()


@patch('file_handler.tk.filedialog.askopenfilename', return_value="")
def test_open_board_dialog_cancel(askopenfilename_mock, file_handler):
    file_handler.load_board = Mock()

    file_handler.open_board_dialog()

    askopenfilename_mock.assert_called_once_with(initialdir="./boards", filetypes=[("Picasso Board", "*.pcso")],
                                                 defaultextension=".pcso")
    file_handler.load_board.assert_not_called()


def test_save_board_empty(file_handler, tmp_path):
    file_handler.canvas.find_all = Mock(return_value=[])
    file_handler.board.objects = []

    file_path = tmp_path / "test_empty.pcso"
    file_handler.save_board(str(file_path))

    with open(file_path, 'r') as f:
        board_state = json.load(f)

    assert board_state == {'objects': []}


def test_load_objects_empty(file_handler):
    objects_state = []
    file_handler.board.objects = []
    file_handler.canvas.create_rectangle = Mock()
    file_handler.canvas.create_text = Mock()

    file_handler.load_objects(objects_state)

    file_handler.canvas.create_rectangle.assert_not_called()
    file_handler.canvas.create_text.assert_not_called()
    assert file_handler.board.objects == []


def test_load_board_file_not_found(file_handler, tmp_path):
    file_path = tmp_path / "nonexistent.pcso"
    with pytest.raises(FileNotFoundError):
        file_handler.load_board(str(file_path))


def test_export_board(file_handler, tmp_path):
    file_handler.canvas.postscript = Mock(return_value="test_postscript")
    file_handler.canvas.find_all = Mock(return_value=[1, 2, 3])
    file_handler.canvas.bbox = Mock(side_effect=[(0, 0, 100, 100), (100, 100, 200, 200),
                                                 (200, 200, 300, 300)])
    file_handler.canvas.type = Mock(
        side_effect=["rectangle", "oval", "line"])
    itemcget_side_effects = {
        (1, "fill"): "red",
        (1, "width"): "2",
        (1, "outline"): "blue",
        (1, "tags"): "tag1",
        (2, "fill"): "green",
        (2, "width"): "3",
        (2, "outline"): "yellow",
        (2, "tags"): "tag2",
        (3, "fill"): "black",
        (3, "width"): "4",
        (3, "outline"): "purple",
        (3, "tags"): "tag3"
    }
    file_handler.canvas.itemcget = Mock(side_effect=lambda obj, attr: itemcget_side_effects[(obj, attr)])
    file_handler.canvas.coords = Mock(side_effect=[(0, 0, 100, 100), (100, 100, 200, 200), (
        200, 200, 300, 300)])

    with patch('file_handler.filedialog.asksaveasfilename', return_value=str(tmp_path / "test_export.png")), \
            patch('PIL.Image.new') as mock_new_image:
        mock_image = Mock()
        mock_new_image.return_value = mock_image

        file_handler.export_board()

        mock_new_image.assert_called_once_with("RGBA", (300, 300), "white")
        mock_image.save.assert_called_once_with(str(tmp_path / "test_export.png"))


def test_export_board_cancel(file_handler):
    with patch('file_handler.filedialog.asksaveasfilename', return_value=""):
        file_handler.canvas.postscript = Mock()

        file_handler.export_board()

        file_handler.canvas.postscript.assert_not_called()


# @patch('file_handler.filedialog.asksaveasfilename', side_effect=[
#     str(tmp_path / "test_export.jpg"),
#     str(tmp_path / "test_export.gif")
# ])
# def test_export_board_file_extensions(asksaveasfilename_mock, file_handler, tmp_path):
#     file_handler.canvas.find_all = Mock(return_value=[])
#     file_handler.canvas.bbox = Mock(return_value=(0, 0, 100, 100))
#
#     with patch('PIL.Image.new') as mock_new_image:
#         mock_image = Mock()
#         mock_new_image.return_value = mock_image
#
#         file_handler.export_board()
#         file_handler.export_board()
#
#         assert asksaveasfilename_mock.call_count == 2
#         mock_image.save.assert_has_calls([
#             call(str(tmp_path / "test_export.jpg")),
#             call(str(tmp_path / "test_export.gif"))
#         ])


def test_export_board_different_object_types(file_handler, tmp_path):
    file_handler.canvas.find_all = Mock(return_value=[1, 2, 3, 4, 5])
    file_handler.canvas.bbox = Mock(side_effect=[(0, 0, 100, 100)] * 5)
    file_handler.canvas.type = Mock(side_effect=["rectangle", "oval", "line", "polygon", "text"])
    itemcget_side_effects = {
        (1, "fill"): "red",
        (1, "width"): "2",
        (1, "outline"): "blue",
        (1, "tags"): "tag1",
        (2, "fill"): "green",
        (2, "width"): "3",
        (2, "outline"): "yellow",
        (2, "tags"): "tag2",
        (3, "fill"): "black",
        (3, "width"): "4",
        (3, "tags"): "tag3",
        (4, "fill"): "orange",
        (4, "width"): "5",
        (4, "outline"): "purple",
        (4, "tags"): "tag4",
        (5, "fill"): "brown",
        (5, "width"): "6",
        (5, "font"): "Arial 12",
        (5, "text"): "Hello",
        (5, "tags"): "tag5"
    }
    file_handler.canvas.itemcget = Mock(side_effect=lambda obj, attr: itemcget_side_effects[(obj, attr)])
    file_handler.canvas.coords = Mock(side_effect=[(0, 0, 100, 100)] * 5)
    with patch('file_handler.filedialog.asksaveasfilename', return_value=str(tmp_path / "test_export.png")), \
            patch('PIL.Image.new') as mock_new_image, \
            patch('PIL.ImageFont.truetype') as mock_truetype:
        mock_image = Mock()
        mock_new_image.return_value = mock_image

        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 100, 20)  # Add this line to provide a return value
        mock_truetype.return_value = mock_font

        file_handler.export_board()

        mock_new_image.assert_called_once_with("RGBA", (100, 100), "white")
        mock_image.save.assert_called_once_with(str(tmp_path / "test_export.png"))


def test_export_board_object_outside_canvas(file_handler, tmp_path):
    file_handler.canvas.find_all = Mock(return_value=[1])
    file_handler.canvas.bbox = Mock(return_value=(-100, -100, 100, 100))
    file_handler.canvas.type = Mock(return_value="rectangle")
    itemcget_side_effects = {
        (1, "fill"): "red",
        (1, "width"): "2",
        (1, "outline"): "blue",
        (1, "tags"): "tag1"
    }
    file_handler.canvas.itemcget = Mock(side_effect=lambda obj, attr: itemcget_side_effects[(obj, attr)])
    file_handler.canvas.coords = Mock(return_value=(-100, -100, 100, 100))

    with patch('file_handler.filedialog.asksaveasfilename', return_value=str(tmp_path / "test_export.png")), \
            patch('PIL.Image.new') as mock_new_image:
        mock_image = Mock()
        mock_new_image.return_value = mock_image

        file_handler.export_board()

        mock_new_image.assert_called_once_with("RGBA", (200, 200), "white")
        mock_image.save.assert_called_once_with(str(tmp_path / "test_export.png"))


def test_load_objects_missing_properties(file_handler):
    objects_state = [
        {'type': 'rectangle', 'coords': [10, 10, 20, 20], 'fill': 'red', 'outline': 'red', 'width': '2', 'z-index': 1},
        {'type': 'text', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 2, 'font': 'Arial 12',
         'text': 'Hello'}
    ]
    file_handler.board.objects = []
    file_handler.canvas.create_rectangle = Mock(return_value=1)
    file_handler.canvas.create_text = Mock(return_value=2)
    font_name = 'Arial'
    size = 12
    pyglet_font = pyglet.font.load(font_name, size)
    file_handler.loaded_fonts = {('Arial', 12): pyglet_font}
    file_handler.load_objects(objects_state)

    assert file_handler.canvas.create_rectangle.call_args_list == [
        call(10, 10, 20, 20, fill='red', outline='red', width='2'),
    ]
    assert file_handler.canvas.create_text.call_args_list == [
        call(30, 30, fill='red', font=('Arial', 12), text='Hello'),
    ]

    assert file_handler.board.objects == [2, 1]


def test_load_board_unsupported_object_types(file_handler, tmp_path):
    board_state = {
        'objects': [
            {'type': 'rectangle', 'coords': [10, 10, 20, 20], 'fill': 'red', 'width': '2', 'z-index': 0,
             'outline': 'blue'},
            {'type': 'unsupported', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 1, 'font': 'Arial 12',
             'text': 'Hello'}
        ]
    }
    file_path = tmp_path / "test_unsupported.pcso"
    with open(file_path, 'w') as f:
        json.dump(board_state, f)

    file_handler.new_board = Mock()
    file_handler.load_objects = Mock()

    file_handler.load_board(str(file_path))

    file_handler.new_board.assert_called_once()
    file_handler.load_objects.assert_called_once_with(board_state['objects'])


def test_save_board_special_characters(file_handler, tmp_path):
    file_handler.canvas.type = Mock(side_effect=["rectangle", "text"])
    file_handler.canvas.coords = Mock(side_effect=[[10, 10, 20, 20], [30, 30]])
    itemcget_side_effects = [
        ["red", "2", "blue"],
        ["red", "2", "Arial 12", "こんにちは"]
    ]
    file_handler.canvas.itemcget = Mock(side_effect=lambda obj, attr: itemcget_side_effects[obj - 1].pop(0))
    file_handler.canvas.find_all = Mock(return_value=[1, 2])
    file_handler.board.objects = [1, 2]

    file_path = tmp_path / "test_special_characters.pcso"
    file_handler.save_board(str(file_path))

    with open(file_path, 'r', encoding='utf-8') as f:
        board_state = json.load(f)

    assert board_state == {
        'objects': [
            {'type': 'rectangle', 'coords': [10, 10, 20, 20], 'fill': 'red', 'width': '2', 'z-index': 0,
             'outline': 'blue'},
            {'type': 'text', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 1, 'font': 'Arial 12',
             'text': 'こんにちは'}
        ]
    }


def test_new_board_already_empty(file_handler):
    file_handler.canvas.delete = Mock()
    file_handler.board.canvas_utils.return_to_middle = Mock()
    file_handler.board.objects = []
    file_handler.board.drawing = False
    file_handler.new_board()

    file_handler.canvas.delete.assert_called_once_with("all")
    assert file_handler.board.objects == []
    assert file_handler.board.drawing is False
    file_handler.board.canvas_utils.return_to_middle.assert_called_once()


def test_load_objects_fallback_font(file_handler):
    objects_state = [
        {'type': 'text', 'coords': [30, 30], 'fill': 'red', 'width': '2', 'z-index': 0, 'font': 'Unknown 12',
         'text': 'Hello'}
    ]
    file_handler.board.objects = []
    file_handler.canvas.create_text = Mock(return_value=1)
    font_name = 'Arial'
    size = 12
    pyglet_font = pyglet.font.load(font_name, size)
    file_handler.loaded_fonts = {('Arial', 12): pyglet_font}
    file_handler.load_objects(objects_state)
    assert file_handler.canvas.create_text.call_args_list == [
        call(30, 30, text='Hello', font=('Arial', 12), fill='red'),
    ]
    assert file_handler.board.objects == [1]


def test_export_board_empty_canvas(file_handler, tmp_path):
    file_handler.canvas.find_all = Mock(return_value=[])
    with patch('file_handler.filedialog.asksaveasfilename', return_value=str(tmp_path / "test_empty.png")), \
            patch('PIL.Image.new') as mock_new_image:
        mock_image = Mock()
        mock_new_image.return_value = mock_image

        file_handler.export_board()

        mock_new_image.assert_called_once_with("RGBA", (200, 200), "white")
        mock_image.save.assert_called_once_with(str(tmp_path / "test_empty.png"))


def test_export_board_skip_selection_eraser_frame(file_handler, tmp_path):
    file_handler.canvas.find_all = Mock(return_value=[1, 2, 3])
    file_handler.canvas.bbox = Mock(side_effect=[(0, 0, 100, 100), (100, 100, 200, 200), (200, 200, 300, 300)])
    file_handler.canvas.type = Mock(side_effect=["rectangle", "oval", "line"])
    itemcget_side_effects = {
        (1, "fill"): "red",
        (1, "width"): "2",
        (1, "outline"): "blue",
        (1, "tags"): "selection_frame",
        (2, "fill"): "green",
        (2, "width"): "3",
        (2, "outline"): "yellow",
        (2, "tags"): "tag2",
        (3, "fill"): "black",
        (3, "width"): "4",
        (3, "tags"): "eraser_frame"
    }
    file_handler.canvas.itemcget = Mock(side_effect=lambda obj, attr: itemcget_side_effects[(obj, attr)])
    file_handler.canvas.coords = Mock(side_effect=[(0, 0, 100, 100), (100, 100, 200, 200), (200, 200, 300, 300)])
    with patch('file_handler.filedialog.asksaveasfilename', return_value=str(tmp_path / "test_export.png")), \
            patch('PIL.Image.new') as mock_new_image:
        mock_image = Mock()
        mock_new_image.return_value = mock_image

        file_handler.export_board()

        mock_new_image.assert_called_once_with("RGBA", (100, 100), "white")
        mock_image.save.assert_called_once_with(str(tmp_path / "test_export.png"))
