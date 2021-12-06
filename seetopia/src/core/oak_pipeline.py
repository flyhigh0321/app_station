import cv2
import sys
import numpy as np
import depthai as dai
from pyzbar import pyzbar
from ..utils import utils  # ..
from ..conf import config  # ..

cfg = config.cfg


class OakPipeline:
    """Creates a :depthai_pipeline:`depthai.Pipeline <>` object which represents
    a pipeline, set of nodes and connections between them.

    Currently, ``color_Cam``, ``mono_left``, ``mono_right`` and ``stereo``
    nodes are configured. More details about the configured nodes can be
    found in the :oak_config:`Miro board <>`.

    Default configurations are loaded from :class:`src.conf.config.CvConfig`

    .. note::
       Nodes are the building blocks when populating the Pipeline. Each node
       provides a specific functionality on the DepthaI, a set of configurable
       properties and inputs/outputs. After creating a node on a pipeline, it
       is possible to configure it as desired and link it to other nodes.

       Pipeline is a collection of nodes and links between them. This flow
       provides extensive flexibility from DepthAI camera.

    Parameters
    ----------
    nn_family : string
        Type of neural network used. Currently ``mobilenet`` is used.
    img_frame: np array
        Its initialised to a np array of 300x300 zeros.During run time, it points
        to input image of size (300,300)
    ORB: :class:`src.utils.utils.FeatureExtraction`
        An instance of :class:`src.utils.utils.FeatureExtraction`  performs feature
        matching using ORB feature detection which consists of three steps, feature
        point extraction, generating feature point descriptors and feature point
        matching.
    label_map: list
        List of output labels for the model
    nn_blob_path:
        path to the saved model (openvino model format)
    threshold1: int
        Minimum threshold value used for canny edge detection
    threshold2: int
        Maximum threshold value used for canny edge detection
    area_min: int
        Area threshold used for contour filtering
    base_depth: int
        Distance between the camera module and flat surface on which the objects
        are placed.
    """

    def __init__(self):
        super(OakPipeline, self).__init__()
        self.nn_family = "mobilenet"
        self.vid_capture = True
        self.img_frame = np.zeros((300, 300, 3), dtype=np.uint8)
        self.ORB = utils.FeatureExtraction(
            utils.relative_to_abs_path(cfg.db.img_class_fpath)
        )
        self.ORB.update_prod_list()
        if cfg.cv.debug:
            print(self.ORB.class_names)
            print(self.ORB.product_list)

        self.label_map = cfg.model.label_map
        self.sync_nn = cfg.calib.syncnn
        self.nn_blob_path = utils.relative_to_abs_path(cfg.model.blob_fpath)
        if len(sys.argv) > 1:
            self.nn_blob_path = sys.argv[1]
        self.threshold1 = cfg.cv.thres_min
        self.threshold2 = cfg.cv.thres_max
        self.area_min = cfg.cv.area_min
        self.base_depth = cfg.calib.base_depth
        self.color = (cfg.cv.r_color, cfg.cv.g_color, cfg.cv.b_color)
        self.scale_factor = [cfg.cv.scale_factor_x, cfg.cv.scale_factor_y]

    def calc_fps(self, counter, start_time, current_time):
        """Calculates the frames per second by dividing the total number of
        rendered frames by elapsed time

        Parameters
        ----------
        counter : int
            Number of rendered frames
        start_time : time
            Time when the first frame was streamed
        current_time : time
            Time when the current frame is streamed.

        Returns
        -------
        int
            Frames per seconds value
        """
        return counter / (current_time - start_time)

    def create_color_cam(self, nodes, pipeline):
        """Creates a ``color_cam`` node, configures the newly created node
        and populates it with existing nodes in  ``depthai pipeline`` after
        establishing connection between them.

        .. note::
            ``color_Cam`` node receives the input frame from the main RGB cam
            in the oak cam and transmit the frames to the connected device
            through the ``XLinkOut`` channel.

        Parameters
        ----------
        nodes :
            Existing nodes in the current pipeline
        pipeline :
            Set of all the nodes and the links between them

        Returns
        -------
        nodes
            Updated nodes with ``color_cam`` node added to it
        pipeline
            Updated depthai nodes and links in the form of a pipeline
        """
        nodes.cam_rgb = pipeline.createColorCamera()
        nodes.cam_rgb.setPreviewSize(
            cfg.model.input_size_x, cfg.model.input_size_y)
        nodes.cam_rgb.setResolution(
            dai.ColorCameraProperties.SensorResolution.THE_1080_P
        )
        nodes.cam_rgb.setInterleaved(cfg.calib.interleaved_color_cam)
        nodes.cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

        nodes.xout_rgb = pipeline.createXLinkOut()
        nodes.xout_rgb.setStreamName("rgb")
        if not self.sync_nn:
            nodes.cam_rgb.preview.link(nodes.xout_rgb.input)
        return nodes, pipeline

    def create_left_cam(self, nodes, pipeline):
        """Creates a ``mono_left`` node, configures the newly created node
        and populate it with existing nodes in  ``depthai pipeline`` after
        establishing connection between them.

        .. note::
            ``mono_left`` node receives the input frame from the left mono cam
            in the oak cam and transmit the frames to the connected device
            through the ``XLinkOut`` channel.

            Please note that the output link of this node is also connected
            with the ``nodes.stereo.left``

        Parameters
        ----------
        nodes :
            Existing nodes in the current pipeline
        pipeline :
            Set of all the nodes and the links between them

        Returns
        -------
        nodes
            Updated nodes with ``mono_left`` node added to it
        pipeline
            Updated depthai nodes and links in the form of a pipeline
        """
        nodes.mono_left = pipeline.createMonoCamera()
        nodes.mono_left.setResolution(
            dai.MonoCameraProperties.SensorResolution.THE_400_P
        )
        nodes.mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        nodes.mono_left.out.link(nodes.stereo.left)
        return nodes, pipeline

    def create_nn_pipeline(self, nodes, pipeline):
        """Creates a ``createMobileNetSpatialDetectionNetwork`` node,
        configures the newly created node and populates it with existing
        nodes in  ``depthai pipeline`` after establishing connection
        between them.

        .. note::
            A ``stereo`` node is also created and connected with the
            ``nn`` node. Please note that different ``nn`` are required for
            differnt family of models.

        Parameters
        ----------
        nodes :
            Existing nodes in the current pipeline
        pipeline :
            Set of all the nodes and the links between them

        Returns
        -------
        nodes
            Updated nodes with ``nn`` node added to it
        pipeline
            Updated depthai nodes and links in the form of a pipeline
        """
        if self.nn_family == "mobilenet":
            nodes.nn = pipeline.createMobileNetSpatialDetectionNetwork()
            nodes.nn.setBlobPath(
                utils.relative_to_abs_path(cfg.model.blob_fpath))
            nodes.nn.setConfidenceThreshold(cfg.calib.thres_conf_spatial)
            nodes.nn.input.setBlocking(cfg.calib.blocking_spatial)
            nodes.nn.setBoundingBoxScaleFactor(
                cfg.calib.bb_scale_factor_spatial)
            nodes.nn.setDepthLowerThreshold(cfg.calib.depth_low_thres_spatial)
            nodes.nn.setDepthUpperThreshold(cfg.calib.depth_high_thres_spatial)

            nodes.xout_nn = pipeline.createXLinkOut()
            nodes.xout_nn.setStreamName("detections")
            nodes.nn.out.link(nodes.xout_nn.input)

            nodes.xout_bb = pipeline.createXLinkOut()
            nodes.xout_bb.setStreamName("boundingBoxDepthMapping")
            nodes.nn.boundingBoxMapping.link(nodes.xout_bb.input)

            nodes.xout_depth = pipeline.createXLinkOut()
            nodes.xout_depth.setStreamName("depth")
            nodes.nn.passthroughDepth.link(nodes.xout_depth.input)

            if self.sync_nn:
                nodes.nn.passthrough.link(nodes.xout_rgb.input)

            # stereo channel
            nodes.stereo = pipeline.createStereoDepth()
            nodes.stereo.setOutputDepth(cfg.calib.output_depth_stereo)
            nodes.stereo.setConfidenceThreshold(cfg.calib.thres_conf_stereo)
            nodes.stereo.depth.link(nodes.nn.inputDepth)
            return nodes, pipeline

    def create_right_cam(self, nodes, pipeline):
        """Creates a ``mono_right`` node, configures the newly created node
        and populate it with existing nodes in  ``depthai pipeline`` after
        establishing connection between them.

        .. note::
            ``mono_right`` node receives the input frame from the right mono cam
            in the oak cam and transmit the frames to the connected device
            through the ``XLinkOut`` channel.

            Please note that the output link of this node is also connected
            with the ``nodes.stereo.right``

        Parameters
        ----------
        nodes :
            Existing nodes in the current pipeline
        pipeline :
            Set of all the nodes and the links between them

        Returns
        -------
        nodes
            Updated nodes with ``mono_right`` node added to it
        pipeline
            Updated depthai nodes and links in the form of a pipeline
        """
        nodes.mono_right = pipeline.createMonoCamera()
        nodes.mono_right.setResolution(
            dai.MonoCameraProperties.SensorResolution.THE_400_P
        )
        nodes.mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        nodes.mono_right.out.link(nodes.stereo.right)
        return nodes, pipeline

    def decode_barcode(self, frame, draw=False):
        """Detects barcode from the given frame and decodes it using
        :pyzbar:`pyzbar`. It also possible to detect and decode more than
        one barcode in the given frame.

        .. note::
            Currently ``QRcode`` and ``EAN13`` are supported. More barcode
            types can be added if required.

            >>> pyzbar.decode(
                    frame,
                    symbols=[
                        pyzbar.ZBarSymbol.QRCODE,
                        pyzbar.ZBarSymbol.EAN13,
                    ],
                )

        Parameters
        ----------
        frame :
            Current frame transmitted from oak cam module
        draw : bool, optional
            If ``True``, it writes the decoded barcode info on the
            given frame, by default False

        Returns
        -------
        string
            Decoded barcode value
        string
            Decoded barcode type
        """
        barcodeData, barcodeType = None, None
        barcodes = pyzbar.decode(
            frame,
            symbols=[
                pyzbar.ZBarSymbol.QRCODE,
                pyzbar.ZBarSymbol.EAN13,
            ],
        )
        img_bar = frame.copy()

        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            if draw:
                cv2.rectangle(img_bar, (x, y), (x + w, y + h), (0, 0, 255), 2)
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(
                    img_bar,
                    text,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )

        return barcodeData, barcodeType

    def draw_measurements(self, frame, detections, object_depth=0, draw=True):
        """Preprocess a given frame  Input image is converted to gray
        scale, gaussian blur, canny edge detection. dilation and erosion are performed
        in the given order before finding contours using :find_contours:`cv2.findContours() <>`

        Rotated bounding box on all the objects that matches the ``min_area`` are fetched
        from  :func:`src.utils.utils.get_bounding_rect`.

        .. note::
            Currently bounding box is drawn for all the objects with matches the ``min_area``
            contour criteria. Function can be modified to draw bounding boxes only for the
            detected objects from the ``nn`` node.

            However, ``depth`` is estimated only for the objects detected by the ``nn`` node.


        Parameters
        ----------
        frame :
            Current frame transmitted from the oak cam module
        detections : list
            List of four corner points detected by the :func:`create_nn_pipeline`
        object_depth : int, optional
            Measured depth of the object from :func:`create_nn_pipeline`,
            by default 0
        draw : bool, optional
            If ``True`` writes the depth value of an object on the current
            frame, by default True

        Returns
        -------
        img
            Processed frame with bounding bax and depth values written
        dict
            Dimensions of the object (length,width,depth)
        """
        obj_l, obj_w, obj_h = 0, 0, 0
        height = frame.shape[0]
        width = frame.shape[1]
        img_wrap = frame.copy()
        img_blur = cv2.GaussianBlur(
            img_wrap,
            (cfg.cv.kernel_gauss, cfg.cv.kernel_gauss),
            cfg.cv.iter_gauss,
        )

        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, self.threshold1, self.threshold2)

        # cv2.imshow("cropped imgCanny", img_canny)

        kernel = np.ones((cfg.cv.kernel_dilate, cfg.cv.kernel_dilate))
        img_dil = cv2.dilate(img_canny, kernel, iterations=cfg.cv.iter_dilate)
        (img_contour, obj_l, obj_w) = utils.get_bounding_rect(
            img_wrap_shadow=img_wrap,
            img=img_dil,
            img_contour=img_wrap,
            scale_factor=self.scale_factor,
            area_min=self.area_min,
            draw=False,
            regular_box=False,
            color=(0, 255, 255),
        )
        for detection in detections:
            # denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            try:

                label = self.label_map[detection.label]
            except:
                label = detection.label
            if label == "greenmat":
                pass
            elif label == "object":
                if object_depth == 0:
                    object_depth = int(detection.spatialCoordinates.z) / 10

                    obj_h = self.base_depth - object_depth
                    if draw:
                        cv2.putText(
                            img_contour,
                            "Z: {:.2f} cm".format(obj_h),
                            (x1 + 18, y1 + 95),
                            cv2.FONT_HERSHEY_TRIPLEX,
                            0.5,
                            self.color,
                        )
        height, width, layers = img_contour.shape
        new_h = height
        new_w = width
        img_contour = cv2.resize(img_contour, (new_w, new_h))
        return img_contour, {"length": obj_l, "width": obj_w, "depth": obj_h}


if __name__ == "__main__":
    OakPipeline().run()
