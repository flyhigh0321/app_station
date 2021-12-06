import kivy
from kivy.uix.screenmanager import Screen
from ..widgets import barcode_popup as bp
from ..widgets import custom_snack_bar as csb
from kivy.core.window import Window
from kivy.clock import Clock
from functools import partial
from .. import config as kivy_config


class DashBoard(Screen):
    """This is the Class object for the ``Main window``.

    .. note::
        Click :dashboard:`here <>` to see ``Dash board`` example.

    Parameters
    ----------
    Screen :
        A relative layout of an empty screen associated with the
        current window.
    popup:
        An instance of :class:`src.ui.widgets.barcode_popup.BarcodePopup`
        to display popups in the current screen.
    config:
        ``kv`` configuration for kivy loaded from a ``yaml`` file.
    fields: dict
        ``widgets`` and therir label names
    m_lables: list
        list of all the ``measure`` widget
    w_lables: list
        list of all the ``weight`` widget (extended ``m_labels``)
    """

    def __init__(self, **kwargs):
        super(DashBoard, self).__init__(**kwargs)
        self.popup = bp.BarcodePopup(text="Unrecognised Barcode")
        self.root = None
        self.config = kivy_config.dashboard_conf
        self.fields = kivy_config.fields
        self.m_labels = ["length", "width", "depth"]
        self.w_labels = ["length", "width", "depth", "act_wgt", "exp_wgt"]
        self.text_ids = []
        self.label_ids = []

    def check_measurements(
        self,
        start_qa,
        master_data,
        window_size,
        dimension={"width": 0, "length": 0, "depth": 0},
    ):
        """Validates the measured dimension with the expected value from ``WMS`` and
        invokes :func:`show_updated_measurements` and :func:`update_labels` functions with
        appropriate ``status`` value ie. ``success`` or ``lapse``.

        .. todo::
            ``weight`` to be auto populated from a digital weighing scale in the future.

            >>> dimension["weight"] = master_data["weight"]
            >>> dimension["item_cnt"] = master_data["quantity"]

        .. note::
            Kivy :clock:`Clock <>` object is used to schedule these function calls once.

        Parameters
        ----------
        start_qa : bool
            Indicates the state of QA
        master_data : dict
            Response from ``WMS`` for a specific ``transfer id``
        window_size : list
            Size of the current window [width, height]
        dimension : dict, optional
            Measured value from :class:`src.core.oak_pipeline.OakPipeline` or
            override value frm user,
            by default {"width": 0, "length": 0, "depth": 0}
        """
        if start_qa:
            # check dim with value from wms
            mismatch = (
                True
                if (
                    float(dimension[feature])
                    >= (float(master_data["dimensions"][feature]) - 0.5)
                    for feature in self.m_labels
                )
                else False
            )
            # print("mismatch", mismatch)
            # print("master data", master_data)
            # for feature in self.m_labels:
            #     print("dimension", dimension[feature])
            #     print("master data", master_data["dimensions"][feature])
            Clock.schedule_once(
                partial(
                    self.show_updated_measurements,
                    override=False,
                    status="success" if not mismatch else "lapse",
                    obj_labels=["measure"],
                )
            )
            Clock.schedule_once(
                partial(
                    self.update_labels,
                    window_size=window_size,
                    status="success" if not mismatch else "lapse",
                    labels=self.m_labels,
                    widgets=["measure"],
                    dim_actl=dimension,
                    dim_exp=master_data["dimensions"],
                )
            )
            # auto populated from electronic weighing scale
            dimension["weight"] = master_data["weight"]
            dimension["item_cnt"] = master_data["quantity"]
            Clock.schedule_once(
                partial(
                    self.update_labels,
                    window_size=window_size,
                    status="lapse",
                    labels=["weight", "item_cnt"],
                    widgets=["weight", "item_cnt"],
                    dim_actl=dimension,
                    dim_exp={
                        "weight": master_data["weight"],
                        "item_cnt": master_data["quantity"],
                    },
                )
            )

    def confirm_override(self, dimensions, window, status="success"):
        """Displays a popup to confirm the ``override`` action.
        Invokes :func:`show_updated_measurements` and :func:`update_labels` functions with
        appropriate ``status`` value ie. ``success`` or ``lapse``.

        .. note::
            Kivy :clock:`Clock <>` object is used to schedule these function calls once.

        Parameters
        ----------
        dimensions : dict
            Updated dimension values
        window :
            Size of the current window .
        status : str, optional
            ``success`` or ``lapse`` , by default "success"
        """
        Clock.schedule_once(
            partial(
                self.show_updated_measurements,
                status=status,
                obj_labels=[
                    "measure",
                    "weight",
                    "item_cnt",
                    "buttons",
                    "putaway",
                    "finish_qa_btn",
                ],
            )
        )
        Clock.schedule_once(
            partial(
                self.update_labels,
                window_size=window,
                labels=self.w_labels,
                status=status,
                widgets=["measure", "weight"],
                dim_actl=dimensions,
            )
        )

    def flag_transfer(self, flag, widget):
        """Flags a particular transfer by replacing the text values of the
        given widget which is usuallya a ``button``

        Parameters
        ----------
        flag : String
            Usually takes value between ``REMOVE`` and ``FLAG``
        widget :
            ID of the ``widget`` whose ``text`` value will be overridden with
            ``flag`` value
        """
        if flag:
            widget.text = "REMOVE"
            Clock.schedule_once(partial(self.show_flag))
        else:
            widget.text = "  FLAG  "
            Clock.schedule_once(
                partial(
                    self.show_flag,
                    text="Product removed from investigation queue",
                    icon="information",
                    color="orange",
                )
            )

    def get_updated_measurements(self, override_master_data, master_data):
        """Updates the  ``override_master_data`` :class:`src.qa_app_demo.MyMainApp`
        object with values from the custom :class:`src.ui.widgets.custom_input_field.CustomInputField`
        of ``length``, ``width``, ``height`` and ``actual weight`` if they exit. Else, it
        takes the value from the ``hint_text`` which is the measured value from
        :class:`src.core.oak_pipeline.OakPipeline`.

        Also validates if the user entered valid measurements before submitting the
        ``override`` button and shows  :class:`src.ui.widgets.custom_snack_bar.CustomSnackbar`
        or :class:`src.ui.widgets.barcode_popup.BarcodePopup` accordingly.

        .. todo::
            Update the expected ``quanity`` and ``weigth`` values from ``WMS``

        .. note::
            Kivy :clock:`Clock <>` object is used to schedule :func:`show_flag` and
            :func:`show_override_popup` calls once.

        Parameters
        ----------
        override_master_data : dict
            Empty :class:`src.qa_app_demo.MyMainApp` object
        master_data : dict
            Expected values from WMS

        Returns
        -------
        dict
            Updated dimension, weight and quantity values.
        """
        for id in range(len(self.text_ids)):
            override_master_data[self.m_labels[id]] = (
                float(self.text_ids[id].text.split("cm")[0])
                if self.text_ids[id].text
                else float(self.text_ids[id].hint_text.split("cm")[0])
            )
        act_w_id = self.config["weight"]["weight_text_field"]["id"]
        # override_master_data["act_wgt"] = (
        #     float(self.ids[act_w_id].text) if self.ids[act_w_id].text else 0
        # )
        if self.ids[act_w_id].text:
            override_master_data["act_wgt"] = float(self.ids[act_w_id].text)
        elif self.ids[act_w_id].hint_text:
            override_master_data["act_wgt"] = float(
                (self.ids[act_w_id].hint_text).split()[0]
            )
        else:
            override_master_data["act_wgt"] = 0
        override_master_data["exp_wgt"] = master_data["weight"]  # from wms
        q_id = self.config["item_cnt"]["item_cnt_text_field"]["id"]
        override_master_data["qnt"] = (
            int(self.ids[q_id].text) if self.ids[q_id].text else 0
        )
        if 0 in list(override_master_data.values()):
            Clock.schedule_once(
                partial(
                    self.show_flag,
                    text="Override failed.Try providing valid measurements.",
                    icon="alert",
                    color="red",
                )
            )
        else:
            Clock.schedule_once(
                partial(
                    self.show_override_popup,
                    dimensions=override_master_data,
                )
            )
        return override_master_data

    def popup_dismiss(self, dt):
        """Dismisses the current popup on the screen"""
        self.popup.dismiss()

    def reset_measure_widget(self):
        """Invokes :func:`show_updated_measurements` with the below attributes.

        >>> override=False,
            status="default",
            obj_labels=[
                "measure"
            ]

        .. note::
            Kivy :clock:`Clock <>` object is used to schedule this function call once.

        """
        Clock.schedule_once(
            partial(
                self.show_updated_measurements,
                override=False,
                status="default",
                obj_labels=[
                    "measure",
                ],
            )
        )

    def show_flag(
        self,
        dt,
        text="Product flagged for further investigation",
        icon="alert",
        color="tomato",
    ):
        """Creates an instance of custom snack bar class
        :class:`src.ui.widgets.custom_snack_bar.CustomSnackbar` and displays it.

        Parameters
        ----------
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        text : str, optional
            Custom text message for :class:`src.ui.widgets.custom_snack_bar.CustomSnackbar`, by default "Product flagged for further investigation"
        icon : str, optional
            Custom icon for :class:`src.ui.widgets.custom_snack_bar.CustomSnackbar`, by default "alert"
        color : str, optional
            custom color for :class:`src.ui.widgets.custom_snack_bar.CustomSnackbar`, by default "tomato"
        """
        snackbar = csb.CustomSnackbar(
            text=text, icon=icon, snackbar_x="10dp", snackbar_y="10dp"
        )
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 150)
        ) / Window.width
        snackbar.pos_hint = {"center_x": 0.885, "center_y": 0.90}
        snackbar.bg_color = kivy.utils.get_color_from_hex(kivy_config.colors[color])
        snackbar.open()

    def show_override_popup(self, dt, dimensions={}):
        """
        Displays an instance of :class:`src.ui.widgets.barcode_popup.BarcodePopup`
        for confirming the ``override`` action invoked by the user by presssing the
        ``override`` button in :class:`src.ui.screens.dashboard.DashBoard` screen.

        When a new updates dimension value is available, product ``dimension``, ``weight``
        and ``quantity`` values are also displayed.

        .. todo::
            Receive ``product name`` from ``WMS``

        Parameters
        ----------
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        dimensions : dict, optional
            Updated dimensions, by default {}
        """
        self.popup.text = "Are you sure you want to override {} information ?".format(
            "Oak-D camera"  # product name from wms
        )
        self.popup.title = "Confirm"

        if dimensions:
            self.popup.ids.product_dimensions.text = (
                "Dimension: {} cm x {} cm x {} cm".format(
                    dimensions["length"], dimensions["width"], dimensions["depth"]
                )
            )
            self.popup.ids.product_weight.text = "Weight: {} g".format(
                dimensions["act_wgt"]
            )
            self.popup.ids.product_quantity.text = "Quantity: {}".format(
                dimensions["qnt"]
            )  # wms
        self.popup.open()

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

    def show_updated_measurements(
        self,
        color="lime green",
        icon="check-circle",
        override=True,
        status="success",
        obj_labels=[
            "measure",
            "weight",
            "item_cnt",
            "buttons",
            "putaway",
            "finish_qa_btn",
        ],
    ):
        """
        Updates the properties of widgets mentioned in the ``obj_label`` attributes
        based on the ``status``.

        .. note::
            when ``override`` is enabled, :func:`flag_transfer` is invoked with a ``success``
            message

        .. todo::
            Send ``update`` request to ``WMS`` when ``override`` is enabled.
            Display ``flag`` messages based on the response from WMS (success,fail)

        Parameters
        ----------
        color : str, optional
            Custom color values for :func:`flag_transfer` , by default "lime green"
        icon : str, optional
            Custom icon value for :func:`flag_transfer`, by default "check-circle"
        override : bool, optional
            When enabled invokes ``update`` request to ``wms``, by default True
        status : str, optional
            It takes two values ``success`` and ``lapse`` for now. More
            options can be added, by default "success"
        obj_labels : list, optional
            List of widgets that has to be updated based on the ``status``,
            by default [ "measure", "weight", "item_cnt", "buttons", "putaway", "finish_qa_btn", ]
        """
        if override:
            # Send update notification to WMS <API CALL>
            # Flag msg based on the update resonse from WMS (succes,fail)
            Clock.schedule_once(
                partial(
                    self.show_flag,
                    text="Override Success. Updated master data in WMS",
                    icon="check-circle",
                    color="lime",
                )
            )
        for obj_label in obj_labels:
            widgets = list(self.config[obj_label].keys())
            for widget in widgets:
                if (
                    type(self.config[obj_label][widget]) == dict
                    and status in self.config[obj_label][widget]
                ):
                    updates = self.config[obj_label][widget][status]
                    id = self.config[obj_label][widget]["id"]
                    for field in updates:
                        prop_val = self.config[obj_label][widget][status][field]
                        if field == "text_color":
                            self.ids[id].text_color = kivy.utils.get_color_from_hex(
                                kivy_config.colors[prop_val]
                            )
                        elif field == "icon":
                            self.ids[id].icon = prop_val
                        elif field == "opacity":
                            self.ids[id].opacity = prop_val
                        elif field == "text":
                            self.ids[id].text = prop_val
                        elif field == "pos_hint":
                            self.ids[id].pos_hint = prop_val
                        elif field == "bold":
                            self.ids[id].bold = prop_val
                        elif field == "font_size":
                            self.ids[id].font_size = prop_val
                        elif field == "error":
                            self.ids[id].error = prop_val
                        elif field == "mode":
                            self.ids[id].helper_text_mode = prop_val
                        elif field == "disabled":
                            self.ids[id].disabled = prop_val

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

    def update_ids(
        self,
        dt,
        ids,
        root,
        text_ids,
        label_ids,
    ):
        """Updated the class objects with the ``root`` , ``text fields ids``, ``labels``
        widget details from the main app class :class:`src.qa_app_demo.MyMainApp`

        Parameters
        ----------
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        ids :
            list of all the widget ids in the current window from the main app class
        root :
            Root id of the current window
        text_ids : list
            list of text field ids from :class:`src.qa_app_demo.MyMainApp`
        label_ids : list
            list of label ids from :class:`src.qa_app_demo.MyMainApp`

        Returns
        -------
        dict
            updated ids
        """
        self.root = root
        self.ids = ids
        self.text_ids = text_ids
        self.label_ids = label_ids
        return self.ids

    def update_labels(
        self,
        dt,
        window_size,
        labels,
        widgets=["measure"],
        status="success",
        dim_actl={"width": 0, "length": 0, "depth": 0, "act_wgt": 0, "exp_wgt": 0},
        dim_exp={"width": 0, "length": 0, "depth": 0, "act_wgt": 0, "exp_wgt": 0},
    ):
        """Updates the :class:`src.ui.widgets.custom_input_field.CustomInputField` and
        ``widget labels`` with the expected value if the status is ``lapse`` or with actual
        values if the status is ``success``

        Parameters
        ----------
        window_size : list
            Size of the window
        labels : [type]
            Usually [length, width,height] can also be extended with additional labels [weight,quantity]
        widgets : list, optional
            List of widgets, by default ["measure"]
        status : str, optional
            ``success`` or ``lapse`` , by default "success"
        dim_actl : dict, optional
            Actual dimension measured, by default {"width": 0, "length": 0, "depth": 0, "act_wgt": 0, "exp_wgt": 0}
        dim_exp : dict, optional
            Expected values, by default {"width": 0, "length": 0, "depth": 0, "act_wgt": 0, "exp_wgt": 0}
        """
        f_ids = ["_label"] if status == "success" else ["_text_field"]
        for widget in widgets:

            if widget == "measure":
                unit = "cm"
            elif widget == "weight":
                unit = "g"
            else:
                unit = ""
            for feature in labels:
                for f_id in f_ids:
                    if feature + f_id in self.config[widget]:
                        id = self.config[widget][feature + f_id]["id"]
                        if feature in dim_actl and status == "success":
                            self.ids[id].text = "{}: {:.2f} {}".format(
                                self.fields[feature], dim_actl[feature], unit
                            )
                        elif feature in dim_actl and status == "lapse":

                            self.ids[id].hint_text = "{:.2f} {}".format(
                                dim_actl[feature], unit
                            )
                            self.ids[id].helper_text = (
                                "Expected: {:.2f}".format(dim_exp[feature])
                                if window_size[0] <= 1000
                                else "Expected: {:.2f} {}".format(
                                    dim_exp[feature], unit
                                )
                            )

    def update_widgets(self):
        """Invokes :func:`show_updated_measurements` with the below attributes.

        >>> override=False,
            status="default",
            obj_labels=[
                "weight",
                "item_cnt",
                "buttons",
                "putaway",
                "finish_qa_btn",
            ]

        .. note::
            Kivy :clock:`Clock <>` object us used to schedule this function call once.

        """
        Clock.schedule_once(
            partial(
                self.show_updated_measurements,
                override=False,
                status="default",
                obj_labels=[
                    "weight",
                    "item_cnt",
                    "buttons",
                    "putaway",
                    "finish_qa_btn",
                ],
            )
        )
