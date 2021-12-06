from kivy.uix.screenmanager import Screen
from ..widgets import barcode_popup as bp  # ..
from kivy.clock import Clock
from functools import partial
import kivy
from .. import config as kivy_config


class SearchPage(Screen):
    """This is the Class object for the ``Main window``.

    .. note::
        Click :search_screen:`here <>` to see ``Search screen`` example.

    Parameters
    ----------
    Screen :
        A relative layout of an empty screen associated with the
        current window.
    popup:
        An instance of :class:`src.ui.widgets.barcode_popup.BarcodePopup`
        to display popups in the current screen.
    nxt_screen:
        Upcoming screen
    root:
        ID of the ``root`` widet of the current window
    name_wid:
        ID of the ``product name`` widget
    sku_wid:
        ID of the ``product sku`` widget
    label_wid:
        ID of the ``weight label`` widget
    icon_wid:
        ID of the ``weight icon`` widget
    """

    def __init__(self, **kwargs):
        super(SearchPage, self).__init__(**kwargs)
        self.popup = bp.BarcodePopup(text="Unrecognised Barcode")
        self.nxt_screen = None
        self.root = None
        self.name_wid = None
        self.sku_wid = None
        self.label_wid = None
        self.icon_wid = None

    def clear_Search_text(self, text_wid):
        """Clears the text entered in a  ``text field``

        Parameters
        ----------
        text_wid :
            ``text field`` id to be cleared
        """
        text_wid.text = ""
        text_wid.error = False

    def popup_dismiss(self, dt):
        """Dismisses the current popup on the screen"""
        self.popup.dismiss()

    def search_transfer_barcode(self, user_name, barcode_data, master_data):
        """Updates ``scan`` widget by invoking call to :func:`update_scan_widget`
        When the scanned ``barcode`` is present in WMS.

        .. note::
            Kivy :clock:`Clock <>` object us used to schedule this function call once.

        ..todo::
            ``GET`` request to WMS

        Parameters
        ----------
        user_name : str
            Name provided by the user
        barcode_data : str
            Decoded barcode information
        master_data : dict
            Expected values from wms

        Returns
        -------
        bool
            Status of the ``QA`` session , ``True`` or ``False``
        """
        start_qa = False
        search_text = barcode_data
        # Api call to wms to fetch details of a stock trasnfer
        wms_response = kivy_config.wms_response
        # Details of a specific transfer
        transfer_details = (
            wms_response[search_text] if search_text in wms_response else None
        )
        if transfer_details:  # WMS <API CALL>
            # need wms response
            master_data = transfer_details
            start_qa = True
            Clock.schedule_once(
                partial(
                    self.update_scan_widget,
                    user_name=user_name,
                    master_data=master_data,
                )
            )
        else:
            content = barcode_data + " not recognised."
            Clock.schedule_once(partial(self.show_popup, content=content))
        return start_qa, master_data

    def search_transfer_id(self, cur_screen, user_name, master_data):
        """Invokes call to the :func:`update_scan_widget` when the search
        ID matches the ``WMS`` data and the ``trasfer state`` is ``awaiting QA``
        else invokes :func:`show_popup` to display the ``transfer state`` which is
        either ``completed`` or ``flagged``.

        .. note::
            Kivy :clock:`Clock <>` object us used to schedule this function call once.

        .. todo::
            ``GET`` request to WMS


        Parameters
        ----------
        cur_screen :
            ID of the current screen
        user_name : string
            ``name`` provided by the user
        master_data : dict
            Expected values from WMS

        Returns
        -------
        bool
            Status of the ``QA`` session , ``True`` or ``False``
        string
           Transfer ID entered in the text field
        dict
            Expected values for the searched transfer ID
        """
        start_qa = False
        master_data = None
        search_text = cur_screen.text
        # Api call to wms to fetch details of a stock trasnfer
        wms_response = kivy_config.wms_response
        # Details of a specific transfer
        transfer_details = (
            wms_response[search_text] if search_text in wms_response else None
        )
        if transfer_details:
            transfer_state = transfer_details["state"]
            if transfer_state == "awaiting qa":
                cur_screen.text = ""
                start_qa = True
                # search_text = str(search_text)
                master_data = transfer_details
                Clock.schedule_once(
                    partial(
                        self.update_scan_widget,
                        user_name=user_name,
                        master_data=master_data,
                    )
                )
            elif transfer_state in ["completed", "flagged"]:
                cur_screen.text = ""
                info = "Transfer ID - " + str(search_text)
                content = "QA " + transfer_state
                Clock.schedule_once(
                    partial(self.show_popup, content=content, info=info)
                )
        else:
            self.text_field_error_management(
                screen=cur_screen,
                error="True",
                error_msg="Enter a valid ID",
            )
        return start_qa, search_text, master_data

    def show_popup(
        self,
        dt,
        content,
        info="Alert",
    ):
        """Displays a poppup with the provided ``content``

        Parameters
        ----------
        content : string
            Message to be displayed in the popup.
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        info : string
            Title to be displayed in the popup.
        """
        self.popup.ids.error_msg.text = content
        if info:
            self.popup.title = info
            self.popup.ids.error_msg.halign = "center"
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

    def update_ids(self, dt, nxt_screen, root, name_wid, sku_wid, label_wid, icon_wid):
        """Updates the class objects with the values passed from the main
        :class:`src.qa_app_demo.MyMainApp` class.
        """
        self.nxt_screen = nxt_screen
        self.root = root
        self.name_wid = name_wid
        self.sku_wid = sku_wid
        self.label_wid = label_wid
        self.icon_wid = icon_wid

    def update_scan_widget(self, dt, user_name, master_data=None):
        """Updates the ``scan`` wiget with the values present in the
        master data.

        .. todo::
            Update value from ``WMS``

        Parameters
        ----------
        user_name : string
            ``name`` provided by the user
        master_data :dict
            Expected values from ``WMS`` , by default None
        """
        self.root.current = "dashboard"
        self.nxt_screen.text = "Hello " + user_name + "!"
        if "name" in master_data:
            self.name_wid.text = "Product Name : {}".format(master_data["name"])
            self.sku_wid.text = "Product SKU : {}".format(master_data["sku"])
        self.label_wid.text_color = kivy.utils.get_color_from_hex(
            kivy_config.colors["green"]
        )  # from cfg
        self.icon_wid.text_color = kivy.utils.get_color_from_hex(
            kivy_config.colors["green"]
        )  # from cfg
