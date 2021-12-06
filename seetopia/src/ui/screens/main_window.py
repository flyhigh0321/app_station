from kivy.uix.screenmanager import Screen
from ..widgets import barcode_popup as bp  # ..


class MainWindow(Screen):
    """This is the Class object for the ``Main window``.

    .. note::
        Click :main_window:`here <>` to see ``Main Screen`` example.

    Parameters
    ----------
    Screen :
        A relative layout of an empty screen associated with the
        current window.
    popup:
        An instance of :class:`src.ui.widgets.barcode_popup.BarcodePopup`
        to display popups in the current screen.
    """

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.username = ""
        self.popup = bp.BarcodePopup(text="Unrecognised Barcode")

    def popup_dismiss(self, dt):
        """Dismisses the current popup on the screen"""
        self.popup.dismiss()

    def show_popup(self, content, dt):
        """Displays a poppup with the provided ``content``

        Parameters
        ----------
        content : string
            Message that has to be displayed in the popup.
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        """
        self.popup.ids.error_msg.text = content
        self.popup.open()

    def text_field_error_management(self, screen, error="False", error_msg=""):
        """Manages the error states of the ``text field`` widget in the
        provided ``widget``

        Parameters
        ----------
        screen :
            ``text field`` widget in the current screen
        error : str, optional
            Error state of the text field, by default "False"
        error_msg : str, optional
            The ``helper text`` that is displayed when the ``error`` state
            is enabled, by default ""
        """
        text_field = screen
        if not error:
            text_field.error = False
            text_field.helper_text_mode = "none"
            text_field.helper_text = " "
        else:
            text_field.error = True
            text_field.helper_text_mode = "persistent"
            text_field.helper_text = error_msg
        text_field.text = ""

    def user_authenticate(self, cur_screen, nxt_Screen, root, session):
        """When the ``name`` entered by the user matches with the ``wms``
        data, navigates to next screen and enables the ``session state``.

        Otherwise, it invokes  :func:`text_field_error_management`.

        .. todo::
            Make API call to ``WMS`` to validate the user information.

        Parameters
        ----------
        cur_screen :
            Current screen which is the ``main window``
        nxt_Screen : [type]
            Success screen which is the ``search`` screen.
        root :
            ``root`` widget which has all the ids of the widgets in a
            specific window
        session : bool
            Indicates the state of the user session


        Returns
        -------
        bool
            Returns if a session state is established or not
        """
        username = cur_screen.text
        if username == "Alex":  # WMS <API CALL>
            self.text_field_error_management(screen=cur_screen)
            root.current = "menu"
            nxt_Screen.text = "Hello " + username + "!"
            session = True
        elif username == None:
            cur_screen.required = True
        else:
            self.text_field_error_management(
                screen=cur_screen,
                error="True",
                error_msg="Enter a valid name",
            )
        return session