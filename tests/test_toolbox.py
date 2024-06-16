import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from toolbox import Toolbox


@pytest.fixture(scope="session")
def toolbox():
    root = tk.Toplevel()
    root.withdraw()
    parent = Mock()
    parent.get_root = Mock(return_value=root)
    toolbox = Toolbox(parent)
    yield toolbox
    root.destroy()


def test_init(toolbox):
    assert toolbox.current_tool == "Pen"
    assert toolbox.tools == ["Select", "Pen", "Erase", "Move", "Fill", "Shapes", "Text"]
    assert toolbox.shapes == ["Rectangle", "Triangle", "Circle", "Line", "Polygon"]
    assert toolbox.pen_width == 5
    assert toolbox.pen_color == "black"
    assert toolbox.fill_color == "black"
    assert toolbox.eraser_width == 20
    assert toolbox.text_color == "black"
    assert toolbox.text_font_name == "Arial"
    assert toolbox.text_font_size == 12
    assert isinstance(toolbox.frame, tk.Frame)
    assert len(toolbox.tool_buttons) == len(toolbox.tools) + len(toolbox.shapes)


def test_set_pen_width(toolbox):
    toolbox.set_pen_width('10')
    assert toolbox.pen_width == 10


def test_select_tool_shapes(toolbox):
    for shape in toolbox.shapes:
        toolbox.select_tool(shape)
        assert toolbox.current_tool == shape
        assert toolbox.tool_buttons[shape].button.cget("bg") == "yellow"
        for other_shape in toolbox.shapes:
            if other_shape != shape:
                assert toolbox.tool_buttons[other_shape].button.cget("bg") == (""
                                                                               "white")


def test_choose_fill_color(toolbox):
    with patch('tkinter.colorchooser.askcolor', return_value=("#00FF00", "#00FF00")):
        toolbox.choose_fill_color()
        assert toolbox.fill_color == "#00FF00"

    with patch('tkinter.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.fill_color
        toolbox.choose_fill_color()
        assert toolbox.fill_color == original_color


def test_select_tool_fill(toolbox):
    toolbox.choose_fill_color = Mock()
    toolbox.select_tool("Fill")
    assert toolbox.current_tool == "Fill"
    toolbox.choose_fill_color.assert_called_once()


def test_return_to_middle(toolbox):
    listener1 = Mock()
    listener2 = Mock()
    toolbox.tool_selected_listeners = [listener1, listener2]
    toolbox.return_to_middle()
    listener1.assert_called_once_with("Return to Middle")
    listener2.assert_called_once_with("Return to Middle")


def test_update_font_name_with_different_values(toolbox):
    toolbox.font_var.set("Courier")
    toolbox.update_font_name(toolbox.font_var)
    assert toolbox.text_font_name == "Courier"

    toolbox.font_var.set("Times New Roman")
    toolbox.update_font_name(toolbox.font_var)
    assert toolbox.text_font_name == "Times New Roman"


def test_update_font_size_with_different_values(toolbox):
    toolbox.size_var.set("16")
    toolbox.update_font_size(toolbox.size_var)
    assert toolbox.text_font_size == 16

    toolbox.size_var.set("24")
    toolbox.update_font_size(toolbox.size_var)
    assert toolbox.text_font_size == 24


def test_select_tool(toolbox):
    toolbox.pen_width_scale.pack = Mock()
    toolbox.color_button.pack = Mock()
    toolbox.shapes_frame.pack_forget = Mock()
    toolbox.font_dropdown.pack_forget = Mock()
    toolbox.size_dropdown.pack_forget = Mock()
    toolbox.text_color_button.pack_forget = Mock()
    toolbox.eraser_width_scale.pack_forget = Mock()
    toolbox.move_frame.pack_forget = Mock()

    toolbox.select_tool("Pen")

    assert toolbox.current_tool == "Pen"
    toolbox.pen_width_scale.pack.assert_called_once()
    toolbox.color_button.pack.assert_called_once()
    toolbox.shapes_frame.pack_forget.assert_called_once()
    toolbox.font_dropdown.pack_forget.assert_called_once()
    toolbox.size_dropdown.pack_forget.assert_called_once()
    toolbox.text_color_button.pack_forget.assert_called_once()
    toolbox.eraser_width_scale.pack_forget.assert_called_once()
    toolbox.move_frame.pack_forget.assert_called_once()


def test_set_eraser_width(toolbox):
    toolbox.set_eraser_width("20")

    assert toolbox.eraser_width == 20


def test_update_font_name(toolbox):
    toolbox.font_var.get = Mock(return_value="Courier")

    toolbox.update_font_name(toolbox.font_var)

    assert toolbox.text_font_name == "Courier"


def test_update_font_size(toolbox):
    toolbox.size_var.get = Mock(return_value="16")
    toolbox.update_font_size(toolbox.size_var)

    assert toolbox.text_font_size == 16


@patch('toolbox.colorchooser.askcolor', return_value=("", "#FF0000"))
def test_choose_text_color(askcolor_mock, toolbox):
    toolbox.choose_text_color()

    askcolor_mock.assert_called_once()
    assert toolbox.text_color == "#FF0000"


def test_choose_pen_color(toolbox):
    with patch('tkinter.colorchooser.askcolor', return_value=("#FF0000", "#FF0000")):
        toolbox.choose_pen_color()
        assert toolbox.pen_color == "#FF0000"

    with patch('tkinter.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.pen_color
        toolbox.choose_pen_color()
        assert toolbox.pen_color == original_color


def test_add_tool_selected_listener(toolbox):
    listener = Mock()

    toolbox.add_tool_selected_listener(listener)

    assert listener in toolbox.tool_selected_listeners


def test_choose_pen_color_with_different_inputs(toolbox):
    with patch('tkinter.colorchooser.askcolor', return_value=("#FF0000", "#FF0000")):
        toolbox.choose_pen_color()
        assert toolbox.pen_color == "#FF0000"

    with patch('tkinter.colorchooser.askcolor', return_value=("#00FF00", "#00FF00")):
        toolbox.choose_pen_color()
        assert toolbox.pen_color == "#00FF00"

    with patch('tkinter.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.pen_color
        toolbox.choose_pen_color()
        assert toolbox.pen_color == original_color


def test_choose_text_color_with_different_inputs(toolbox):
    with patch('toolbox.colorchooser.askcolor', return_value=("#0000FF", "#0000FF")):
        toolbox.choose_text_color()
        assert toolbox.text_color == "#0000FF"

    with patch('toolbox.colorchooser.askcolor', return_value=("#FFFF00", "#FFFF00")):
        toolbox.choose_text_color()
        assert toolbox.text_color == "#FFFF00"

    with patch('toolbox.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.text_color
        toolbox.choose_text_color()
        assert toolbox.text_color == original_color


def test_add_tool_selected_listener_multiple_listeners(toolbox):
    listener1 = Mock()
    listener2 = Mock()
    listener3 = Mock()

    toolbox.add_tool_selected_listener(listener1)
    toolbox.add_tool_selected_listener(listener2)
    toolbox.add_tool_selected_listener(listener3)

    assert listener1 in toolbox.tool_selected_listeners
    assert listener2 in toolbox.tool_selected_listeners
    assert listener3 in toolbox.tool_selected_listeners


def test_select_tool_with_invalid_tool_name(toolbox):
    toolbox.pen_width_scale.pack_forget = Mock()
    toolbox.color_button.pack_forget = Mock()
    toolbox.shapes_frame.pack_forget = Mock()
    toolbox.font_dropdown.pack_forget = Mock()
    toolbox.size_dropdown.pack_forget = Mock()
    toolbox.text_color_button.pack_forget = Mock()
    toolbox.eraser_width_scale.pack_forget = Mock()
    toolbox.move_frame.pack_forget = Mock()
    with pytest.raises(KeyError):
        toolbox.select_tool("InvalidTool")


def test_select_tool_button_configuration(toolbox):
    toolbox.select_tool("Pen")
    assert toolbox.tool_buttons["Pen"].button.cget("bg") == "yellow"
    for tool in toolbox.tools:
        if tool != "Pen":
            assert toolbox.tool_buttons[tool].button.cget("bg") == "white"

    toolbox.select_tool("Erase")
    assert toolbox.tool_buttons["Erase"].button.cget("bg") == "yellow"
    for tool in toolbox.tools:
        if tool != "Erase":
            assert toolbox.tool_buttons[tool].button.cget("bg") == "white"


def test_toolbox_widget_creation(toolbox):
    assert toolbox.pen_button.winfo_exists()
    assert toolbox.color_button.winfo_exists()
    assert toolbox.eraser_button.winfo_exists()
    assert toolbox.return_to_middle_button.winfo_exists()
    assert toolbox.text_button.winfo_exists()
    assert toolbox.font_dropdown.winfo_exists()
    assert toolbox.size_dropdown.winfo_exists()
    assert toolbox.text_color_button.winfo_exists()

    for shape in toolbox.shapes:
        assert toolbox.tool_buttons[shape].button.winfo_exists()


def test_choose_pen_color_no_color_selected(toolbox):
    with patch('tkinter.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.pen_color
        toolbox.choose_pen_color()
        assert toolbox.pen_color == original_color


def test_choose_text_color_no_color_selected(toolbox):
    with patch('toolbox.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.text_color
        toolbox.choose_text_color()
        assert toolbox.text_color == original_color


def test_tool_buttons_creation(toolbox):
    assert len(toolbox.tool_buttons) == len(toolbox.tools) + len(toolbox.shapes)
    for tool in toolbox.tools:
        assert tool in toolbox.tool_buttons
    for shape in toolbox.shapes:
        assert shape in toolbox.tool_buttons


def test_tool_button_command(toolbox):
    toolbox.select_tool = Mock()
    for tool, button_item in toolbox.tool_buttons.items():
        button = button_item.button
        button.invoke()
        toolbox.select_tool.assert_called_with(tool)


def test_choose_fill_color_no_color_selected(toolbox):
    with patch('tkinter.colorchooser.askcolor', return_value=(None, None)):
        original_color = toolbox.fill_color
        toolbox.choose_fill_color()
        assert toolbox.fill_color == original_color
