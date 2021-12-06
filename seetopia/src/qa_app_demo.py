import os

# os.environ["KIVY_NO_ARGS"] = "1"
import kivy
from kivy.config import Config

# # Setting config objects before kivy imports
Config.set("graphics", "minimum_width", "800")
Config.set("graphics", "minimum_height", "600")

# Kivy class object imports
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.resources import resource_add_path

# Kivy MD property object imports
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.snackbar import BaseSnackbar
from kivy.uix.screenmanager import Screen, ScreenManager

# Python modules
import os
import sys
import threading
import depthai as dai
from functools import partial

# Helper module imports
from conf import config
from utils import utils

# from .utils import resource_paths as rp
from core import oak_pipeline as op

# Kivy custom screen,widgets imports
from ui.screens import main_window as mw
from ui.screens import search_page as sp
from ui.screens import dashboard as dashb
from ui.widgets.barcode_popup import BarcodePopup
from ui.widgets.custom_input_field import CustomInputField
from ui.widgets.custom_snack_bar import CustomSnackbar

# Hydra configuration file initialisation
cfg = config.cfg
username = ""
search_field = ""

# Main kv file import
kv = utils.relative_to_abs_path("src/ui/screens/kv/screen_manager.kv")


class QAApp(MDApp):
    """
     This is an instance of :mdapp:`MDApp <>` class and it is used to create and run the kivy application's life cycle.

    .. note::
        Please refer to ``help(QAApp)`` to know more.

    Parameters
    ----------
    MDApp : :kivyapp:`App <>`
        It is inherited from Kivy
        :kivyapp:`App <>` class
    flag : boolean
        ``True`` if an item is flagged for further investigation
        ``False`` otherwise. Typically triggered from the :class:`src.ui.screens.dashboard.DashBoard` screen.
    start_qa: boolean
        ``True`` if a new transfer id is searched / barcode is scanned
        ``False`` if QA is completed or on page refresh
        Usually by clicking the "Done" or "Back" buttons in the :class:`src.ui.screens.dashboard.DashBoard` screen.
    session_state: boolean
        ``True`` if a user logs in
        ``False`` otherwise.
    update_dimension: boolean
        ``True`` if update dimensions are required from OAK pipeline
        ``False`` once the user navigates to the :func:`show_override_popup`.
    barcodeData: str
        Decoded barcode data.
        Currently, it supports a single barcode decoding and can be extended for multiple barcodes.
        Futuristic data type can be a array of strings for multiple barcode decoding.
    master_data: dict
        Json WMS response speicfic to a ``transfer id``.
    dimension: dict
        Measured dimensions (length, width, height) from OAk.
    override_master_data: dict
        Updated master data (length, width, height,weight, quantity)
    window_size: tuple
        Size of the kivy window
    window_w: int
        Width of current kivy window
    window_h: int
        Height of current kivy window
    _keyboard_press: int
        Private variable to capture the key press ids
    oak: :class:`src.core.oak_pipeline.OakPipeline`
        instance of :class:`src.core.oak_pipeline.OakPipeline`
    """

    def __init__(self, **kwargs):
        """
        This is a constructor method.

        """

        super(QAApp, self).__init__(**kwargs)
        self.flag = True
        self.start_qa = False
        self.barcodeData = None
        self.session_state = None
        self.update_dimension = True
        self.dimension = {}
        self.master_data = {}
        self.override_master_data = {}
        self._keyboard_press = None
        self.window_size = Window.size
        self.window_w = Window.width
        self.window_h = Window.height
        self.oak = op.OakPipeline()

        Window.bind(on_key_down=self._keydown)
        Window.bind(on_resize=self._update_window_size)

    def _display_frame(self, frame, dt):
        """
        Creates a new texture in the current page corresponding to
        the size of the processed CV frame and convert it to a byte stream.
        Replace the texture of the `vid` widget of the curernt screen.

        Parameters
        ----------
        frame : np array
            processed cv frame to be streamed
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        """
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(
            frame.tobytes(order=None), colorfmt="bgr", bufferfmt="ubyte"
        )
        texture.flip_vertical()
        current = self.root.current
        self.root.get_screen(current).ids.vid.texture = texture

    def _keydown(self, *args):
        """
        Fired when a new key is pressed down on a
        keybaord binded to the current window
        """
        self._keyboard_press = args[1]

    def _show_dashboard(self, dt):
        """
        Updates the ``measure`` widget (labels and text fields) in the
        :class:`src.ui.screens.dashboard.DashBoard` screen by triggering the
        :func:`src.ui.screens.dashboard.DashBoard.check_measurements` method.

        Parameters
        ----------
        dt : float
            Refers to delta-time for scheduled call back.
        """
        current = self.root.current
        self._update_window_size()
        if current == "dashboard":
            self.root.get_screen("dashboard").check_measurements(
                start_qa=self.start_qa,
                master_data=self.master_data,
                window_size=self.window_size,
                dimension=self.dimension,
            )

    def _start_pipeline(self):
        """
        Configure the ``color_Cam``, ``nn``, ``stereo``, ``mono_left`` and ``mono_right`` nodes.
        Starts the depthai pipeline and process the streaming data from OAK cam.
        Receives the ``preview``, ``detection`` queue and streams the processed frame.
        Decodes the barcode captured in the ``CvFrame`` and updates the ``barcodeData``
        and ``dimension`` attributes.

        If the ``session_state`` is ``True`` and when the decoded ``barcodeData`` is
        available, it triggers the aaaa
        method to initiate the QA.

        """
        self.vid_capture = True
        sync_nn = cfg.calib.syncnn
        pipeline = dai.Pipeline()
        # Create cam nodes
        color_cam = pipeline.createColorCamera()
        nn = pipeline.createMobileNetSpatialDetectionNetwork()
        mono_left = pipeline.createMonoCamera()
        mono_right = pipeline.createMonoCamera()
        stereo = pipeline.createStereoDepth()
        # Create output stream links from oak
        xout_rgb = pipeline.createXLinkOut()
        xout_nn = pipeline.createXLinkOut()
        # Rename the streams
        xout_rgb.setStreamName("rgb")
        xout_nn.setStreamName("detections")
        # Configure color_Cam node
        color_cam.setPreviewSize(cfg.model.input_size_x, cfg.model.input_size_y)
        color_cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        color_cam.setInterleaved(cfg.calib.interleaved_color_cam)
        color_cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        # Configure mono cams
        mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        # setting node configs
        stereo.setOutputDepth(cfg.calib.output_depth_stereo)
        stereo.setConfidenceThreshold(cfg.calib.thres_conf_stereo)
        # Configure neural network node
        nn.setBlobPath(utils.relative_to_abs_path(cfg.model.blob_fpath))
        nn.setConfidenceThreshold(cfg.calib.thres_conf_spatial)
        nn.input.setBlocking(cfg.calib.blocking_spatial)
        nn.setBoundingBoxScaleFactor(cfg.calib.bb_scale_factor_spatial)
        nn.setDepthLowerThreshold(cfg.calib.depth_low_thres_spatial)
        nn.setDepthUpperThreshold(cfg.calib.depth_high_thres_spatial)
        # Create outputs stream links for mono cams
        mono_left.out.link(stereo.left)
        mono_right.out.link(stereo.right)

        color_cam.preview.link(nn.input)
        if sync_nn:
            nn.passthrough.link(xout_rgb.input)
        else:
            color_cam.preview.link(xout_rgb.input)

        nn.out.link(xout_nn.input)
        stereo.depth.link(nn.inputDepth)

        # start processing loop
        with dai.Device(pipeline) as device:
            # Start pipeline
            device.startPipeline()
            # Output queues will be used to get the rgb frames and nn data from the outputs defined above
            preview_queue = device.getOutputQueue(
                name="rgb",
                maxSize=cfg.calib.out_queue_max_size,
                blocking=cfg.calib.out_queue_blocking,
            )
            detection_nn_queue = device.getOutputQueue(
                name="detections",
                maxSize=cfg.calib.out_queue_max_size,
                blocking=cfg.calib.out_queue_blocking,
            )
            frame = None
            detections = []
            while self.oak.vid_capture:
                in_preview = preview_queue.get()
                in_nn = detection_nn_queue.get()
                frame = in_preview.getCvFrame()
                detections = in_nn.detections
                # Decode captured barcode from CV frame
                self.barcodeData, barcodeType = self.oak.decode_barcode(frame)
                img_contour, oak_dim = self.oak.draw_measurements(frame, detections)
                Clock.schedule_once(partial(self._display_frame, img_contour))
                if self.update_dimension:
                    self.dimension = oak_dim
                if self.session_state:
                    if self.barcodeData:
                        self.start_qa, self.master_data = self.root.get_screen(
                            "menu"
                        ).search_transfer_barcode(
                            user_name=self.user_name,
                            barcode_data=self.barcodeData,
                            master_data=self.master_data,
                        )
                    if (
                        self.dimension
                        and self.start_qa
                        and self.root.current == "dashboard"
                    ):

                        if self.update_dimension:
                            Clock.schedule_once(partial(self._show_dashboard))

    def _update_dashboard_ids(self, dt):
        """
        Updates the text and label ids in the :class:`src.ui.screens.dashboard.DashBoard`.
        Scheduled function calls with default values are made using
        :func_partial:`functools.partial <>`

        Parameters
        ----------
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        """
        ids = self.root.get_screen("dashboard").ids
        # print(ids)
        Clock.schedule_once(
            partial(
                self.root.get_screen("dashboard").update_ids,
                ids=ids,
                root=self.root,
                text_ids=[
                    self.root.get_screen("dashboard").ids.length_text_field,
                    self.root.get_screen("dashboard").ids.width_text_field,
                    self.root.get_screen("dashboard").ids.depth_text_field,
                ],
                label_ids=[
                    self.root.get_screen("dashboard").ids.item_length,
                    self.root.get_screen("dashboard").ids.item_width,
                    self.root.get_screen("dashboard").ids.item_depth,
                ],
            )
        )

    def _update_search_page_ids(self, dt):
        """
        Updates the widget ids in the :class:`src.ui.screens.dashboard.DashBoard`.
        Scheduled function calls with default values are made using
        :func_partial:`functools.partial <>`

        Parameters
        ----------
        dt : float
            Refers to delta-time, which is the elapsed time between the
            scheduling and the callback
        """
        Clock.schedule_once(
            partial(
                self.root.get_screen("menu").update_ids,
                nxt_screen=self.root.get_screen("dashboard").ids.userWelcomeName,
                root=self.root,
                name_wid=self.root.get_screen("dashboard").ids.product_name,
                sku_wid=self.root.get_screen("dashboard").ids.product_sku,
                label_wid=self.root.get_screen("dashboard").ids.scan_status,
                icon_wid=self.root.get_screen("dashboard").ids.scan_status_icon,
            )
        )

    def _update_window_size(self, *args):
        """
        Updates class variables with the lastest window size
        """
        self.window_size = Window.size
        self.window_w = Window.width
        self.window_h = Window.height

    def build(self):
        """
        Builds a `parser` for parsing the main `kv` file by using the global kivy
        :builder:`Builder <>` instance.
        Creates a :screen_manager:`Screenmanager <>` and adds the
        :class:`src.ui.screens.main_window.MainWindow`,
        :class:`src.ui.screens.search_page.SearchPage` and
        :class:`src.ui.screens.dashboard.DashBoard` objects to the
        main `root` widget.

        .. note::
            The standard ``theme_cls`` inherited from :mdapp:`MDApp <>` is designed to provide the standard themes
            and colors as defined by Material Design.

            >>> self.theme_cls.primary_palette = "Teal"
            >>> self.theme_cls.primary_hue = "500"

        Returns
        -------
        kv layout
            Returns the root layout of the main kivy app


        """

        threading.Thread(target=self._start_pipeline, daemon=True).start()
        self.layout = Builder.load_file(kv)
        self.root = ScreenManager()
        self.root.add_widget(mw.MainWindow(name="login"))
        self.root.add_widget(sp.SearchPage(name="menu"))  # change to search page
        self.root.add_widget(dashb.DashBoard(name="dashboard"))
        Window.clearcolor = (0.9, 0.9, 0.9, 1)
        Clock.schedule_once(partial(self._update_search_page_ids))
        Clock.schedule_once(partial(self._update_dashboard_ids))
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "500"
        return self.layout

    def clear_measure_widget(self):
        """
        Updates the values of the ``measure`` widget by calling
        :func:`src.ui.screens.dashboard.DashBoard.reset_measure_widget()` method
        """
        current = self.root.current
        self.root.get_screen("dashboard").reset_measure_widget()

    def clear_search_text(self):
        """
        Resets the ``search`` widget by calling
        :func:`clear_search_text` method
        """
        current = self.root.current
        self.root.get_screen(current).clear_Search_text(
            text_wid=self.root.get_screen(current).ids.search_field
        )

    def clear_states(self):
        """Flushes out the states set during the QA process"""
        self.start_qa = False
        self.barcodeData = None
        self.dimension = {}
        self.update_dimension = True

    def clear_weight_widget(self):
        """
        Updates the values of the ``weight`` widget by calling
        :func:`src.ui.screens.dashboard.DashBoard.update_widgets` method
        """
        current = self.root.current
        self.root.get_screen("dashboard").update_widgets()

    def confirm_override(self):
        """
        Submits the updated values to WMS internally by
        triggering :func:`src.ui.screens.dashboard.DashBoard.confirm_override` method
        """

        current = self.root.current
        if current == "SearchPage":
            self.popup_dismiss()
        elif current == "dashboard":
            self.root.get_screen(current).confirm_override(
                dimensions=self.override_master_data,
                window=self.window_size,
                status="success",
            )
            self.update_dimension = False

    def flag_transfer(self):
        """Updates the state of the ``flag`` attribute """
        current = self.root.current
        self.root.get_screen(current).flag_transfer(
            flag=self.flag,
            widget=self.root.get_screen(current).ids.flag_transfer,
        )
        self.flag = not self.flag

    def login_keydown(self):
        """
        Detects the ``Enter`` key press and triggers :func:`user_authenticate()`
        """
        if self._keyboard_press == 13:
            self.user_authenticate()

    def popup_dismiss(self):
        """Dismiss popup in :class:`src.ui.screens.search_page.SearchPage` and
        :class:`src.ui.screens.dashboard.DashBoard` screens"""
        current = self.root.current
        Clock.schedule_once(partial(self.root.get_screen(current).popup_dismiss))

    def rail_open(self):
        """Opens/closes the navigation rail by updating its state to close/open"""
        current = self.root.current
        if self.root.get_screen(current).ids.rail.rail_state == "open":
            self.root.get_screen(current).ids.rail.rail_state = "close"
        else:
            self.root.get_screen(current).ids.rail.rail_state = "open"

    def search_transfer(self):
        """
        Redirects the search request to :class:`src.ui.screens.search_page.SearchPage`
        screen. On successful search, ``start_qa``, ``transfer_ID`` and ``master_data``
        attributes are updated. Otherwise left with the defualt values.
        """
        current = self.root.current
        self.master_data = {}
        self.start_qa, self.transfer_ID, self.master_data = self.root.get_screen(
            current
        ).search_transfer_id(
            cur_screen=self.root.get_screen(current).ids.search_field,
            user_name=self.user_name,
            master_data=self.master_data,
        )

    def show_override_popup(self):
        """
        Displays the override confirmation popup
        by triggering the
        :func:`src.ui.screens.dashboard.DashBoard.get_updated_measurements` method.
        """
        current = self.root.current
        self.override_master_data = {}
        if current == "dashboard":
            self.override_master_data = self.root.get_screen(
                current
            ).get_updated_measurements(
                self.override_master_data,
                master_data=self.master_data,
            )

    def user_authenticate(self):
        """
        Captures the `user name` entered by the user from the
        :class:`src.ui.screens.main_window.MainWindow` screen and
        triggers the :func:`user_authenticate()`
        method for authentication
        """
        self.user_name = self.root.get_screen("login").ids.username.text
        self.session_state = self.root.get_screen("login").user_authenticate(
            cur_screen=self.root.get_screen("login").ids.username,
            nxt_Screen=self.root.get_screen("menu").ids.userWelcomeName,
            root=self.root,
            session=self.session_state,
        )


if __name__ == "__main__":

    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))
    QAApp().run()
