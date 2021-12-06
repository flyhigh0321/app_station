import kivy
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty


class BarcodePopup(Popup):
    """Creates modal popups. Any click outside the window will
    deactivate the popup.

    .. note::
        The default size of a Widget is size_hint=(1, 1).
        The size of the popup can be controlled by changing the
        values of ``size_hint`` (for instance size_hint=(.8, .8)) or
        by deactivating the size_hint and instead using fixed size attributes.

        ``text`` and ``title`` of the popup can be customised with the
        current configuration.

    """

    text = StringProperty(None)
    title = StringProperty()