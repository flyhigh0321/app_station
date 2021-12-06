from kivymd.uix.snackbar import BaseSnackbar
from kivy.properties import StringProperty, NumericProperty


class CustomSnackbar(BaseSnackbar):
    """Provides brief messages, similar to flash cards

    .. note::
        ``text``, ``icon`` and ``font_size`` of the snackbar
        can be customised with the current configuration.
    """

    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")