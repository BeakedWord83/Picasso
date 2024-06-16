from unittest.mock import patch

from main import main


@patch('tkinter.Tk')
@patch('main.App')
def test_main(mock_app, mock_tk):
    main()
    mock_tk.assert_called_once()
    mock_app.assert_called_once_with(mock_tk.return_value)
    mock_tk.return_value.mainloop.assert_called_once()
