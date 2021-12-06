import os
import hydra
import cv2
import numpy as np
from pathlib import Path
from hydra import utils as hy


class FeatureExtraction:
    """This class object performs feature matching using ORB feature detection
    which consists of three steps, feature point extraction, generating feature
    point descriptors and feature point matching. Read more about :orb:`ORB <>`.

    .. note::
        Oriented FAST and Rotated BRIEF (ORB) is an viable alternative to SIFT and SURF.
        ORB was conceived mainly because SIFT and SURF are patented algorithms. ORB is
        better than SURF for feature extraction tasks while being almost two orders of
        magnitude faster.

    Parameters
    ----------
    path :
        File path to the list of images used in feature extraction
    images: img
        Images from the provided file path are extracted here for
        feature extraction and feature point matching.
    class_names: list
        Carries the list of all the unique class names to describe
        and identify an image from any given file path.
    des_list: list
        Stores the extracted feature point descriptors
    product_list: list
        Points to the list of images in the given file path
    orb: :orb_class:`ORB <>`
        Class implementing the :orb:`ORB <>` (oriented BRIEF) keypoint detector and descriptor extractor

    """

    def __init__(self, path):
        self.file_path = path
        self.images = []
        self.class_names = []
        self.des_list = []
        self.product_list = os.listdir(path)
        self.orb = cv2.ORB_create(nfeatures=1000)

    def __resize_image(self, scale, img):
        """
        Resizes a given image ie. either shrink or scale up to meet the size
        requirements.

        Parameters
        ----------
        scale : [float,float]
            The factor by which the image size has to be changed (% change).
            It is determined by the base height of the OAK cam from the objects
            on focus. Separate scale values for x and y axis is expected.
            Currently configured to ``0.92`` for both the axis. To modify the values
            refer to :class:`src.conf.config.CvDefaultConfig`.
        img :
            Image that needs to be resized.

        Returns
        -------
        img
            Returns a resized image by scale factor.
        """
        width = int(img.shape[1] * scale / 100)
        height = int(img.shape[0] * scale / 100)
        dim = (width, height)
        img_resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        return img_resized

    def find_descriptors(self, images):
        """Finds keypoints in an image and computes their descriptors.
        Refer to :orb_detect:`orb_detect <>` for more info.

        Parameters
        ----------
        images : list
            List of images
        """
        for img in images:
            keys, des = self.orb.detectAndCompute(img, None)
            self.des_list.append(des)

    def multiple_product_id(self, img, display=False, thres=15, scale=100):
        """Computes key point descriptor for a given image and uses
        :bf_matcher:`Brute-Force MAtcher <>` to match features from one
        image with a list of images.

        .. note::
            Brute-Force matcher is simple. It takes the descriptor of one feature
            in first set and is matched with all other features in second set using
            some distance calculation. And the closest one is returned.

        The matcher returns only those matches with value (i,j), such that i-th descriptor
        in set A has j-th descriptor in set B as the best match and vice versa.
        That is, the two features in both sets should match each other.

        ``BFMatcher.knnMatch()`` is used to find k best matches where k can be specified.
        The current value of k is 2.0.

        Parameters
        ----------
        img : img
            Input image for feature extraction and matching with existing img dataset.
        display : bool, optional
            If ``True`` matches are drawn on input image and displayed in a window,
            by default False
        thres : int, optional
            Threshold value to filter images, by default 15
        scale : int, optional
            Scale factor for image resizing, by default 100

        Returns
        -------
        list
            Returns a filtered list of best image matches.
        """
        keys, des_cur = self.orb.detectAndCompute(img, None)
        if display:
            img_des = cv2.drawKeypoints(img, keys, None)
            img_des_resized = self.__resize_image(scale, img_des)
            cv2.imshow("Detected Features", img_des_resized)

        bf = cv2.BFMatcher()
        final_val_list = []
        match_list = []
        try:
            for des in self.des_list:
                matches = bf.knnMatch(des, des_cur, k=2)
                best = []
                for m, n in matches:
                    if m.distance < 0.70 * n.distance:
                        best.append([m])
                match_list.append(len(best))
        except:
            # Need to be logged
            pass

        if len(match_list) != 0:
            for i in match_list:
                if i > thres:
                    final_val_list.append(match_list.index(i))

        return final_val_list

    def show_features(self, img1, img2, scale=100):
        """Computes key point descriptor for a given image and uses
        :bf_matcher:`Brute-Force MAtcher <>` to match features from one
        image with another image.

        .. note::
            Refer to :func:`multiple_product_id` for more info.

        Parameters
        ----------
        img1 :
            input image for key point matching
        img2 :
            input image for key point matching
        scale : int, optional
            Scale factor for image resizing, by default 100
        """
        kp1, des1 = self.orb.detectAndCompute(img1, None)
        kp2, des2 = self.orb.detectAndCompute(img2, None)
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        best = []
        for m, n in matches:
            if m.distance < 0.70 * n.distance:
                best.append([m])
        drawn_matches = cv2.drawMatchesKnn(
            img1, kp1, img2, kp2, matches[:10], None, flags=2
        )
        drawn_matches_resized = self.__resize_image(scale, drawn_matches)
        cv2.imshow("Feature Matching", drawn_matches_resized)

    def update_prod_list(self):
        """Extracts images and class names from a directory and updates
        the class objects. Invokes the :func:`find_descriptors` after
        updating the class objects.

        """
        path = self.file_path
        for prod in self.product_list:
            img = cv2.imread(f"{path}/{prod}", 0)
            self.images.append(img)
            self.class_names.append(os.path.splitext(prod)[0])
        self.find_descriptors(self.images)


def find_distance(p1, p2):
    """This function is used to measure the euclidean distance between two corner points.

    Parameters
    ----------
    p1 : list, [int,int]
        x and y co-ordinates of point 1
    p2 : list, [int,int]
        x and y co-ordinates of point 2

    Returns
    -------
    float
        Euclidean distance between two points
    """
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5


def find_distance_abs(p1, p2):
    """Returns absolute distance between two points

    Parameters
    ----------
    p1 : list, [int,int]
        x and y co-ordinates of point 1
    p2 : list, [int,int]
        x and y co-ordinates of point 2

    Returns
    -------
    float
        Absolute distance between two points
    """
    return abs(p1 - p2)


def get_bounding_rect(
    img_wrap_shadow,
    img,
    img_contour,
    scale_factor,
    area_min,
    draw=False,
    regular_box=False,
    color=(114, 143, 155),
):
    """This function finds the contours in a the given wrapped image using
    :find_contours:`cv2.findContours <>` function. Finds the area of all the derived
    contours and filters the contours with a certain ``area_min``.

    .. note::
        If ``regular_box`` is enabled, it draws a regular rectangular bounding box
        else, it draws a rotated bounding box aligned with the orientation of the
        contour points

    Finds the disatance between the corner points using :func:`src.utils.utils.find_distance`
    and writes the measured ``length`` and ``width`` value on the input image.

    Draws an arrowed line to indicate the corners.

    Parameters
    ----------
    img_wrap_shadow : img
        Wrapped image on which the bounding box and measurements will be written
    img : img
        Actual image
    img_contour : img
        Pre processed image for finding contours
    scale_factor : float
        Scale factor used in distance measured. The measured values need to be scaled
        to the size of the image
    area_min : int
        Area threshold to filter the contour points
    draw : bool, optional
        When enabled, draws contour on the ``img_contour``
    regular_box : bool, optional
        When enabled draws a regular bounding box instead of
        rotated bounding box, by default False
    color : tuple, optional
        Choice of color for bounding box, by default (114, 143, 155)

    Returns
    -------
    img
        Processed output img where the bounding box and measured values are drawn
    float
        Measured length value
    float
        Measured width value
    """
    obj_l, obj_w = 0, 0
    color_text = (255, 255, 255)
    contours, hierarchy = cv2.findContours(
        img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area > area_min:
            if draw:
                cv2.drawContours(img_contour, cnt, -1, color, 7)

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)

            # Regular Bounding Box
            if regular_box:
                cv2.rectangle(img_wrap_shadow, (x, y), (x + w, y + h), color, 2)

            # Rotated Bounding Rectangle
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(img_wrap_shadow, [box], 0, color, 2)

            ordered_points = re_order(box)

            obj_l = round(
                (
                    find_distance(
                        ordered_points[0] // scale_factor[0],
                        ordered_points[1] // scale_factor[0],
                    )
                    / 10
                ),
                1,
            )
            obj_w = round(
                (
                    find_distance(
                        ordered_points[0] // scale_factor[1],
                        ordered_points[2] // scale_factor[1],
                    )
                    / 10
                ),
                1,
            )

            cv2.arrowedLine(
                img_wrap_shadow,
                (ordered_points[0][0], ordered_points[0][1]),
                (ordered_points[1][0], ordered_points[1][1]),
                color,
                3,
                8,
                0,
                0.05,
            )
            cv2.arrowedLine(
                img_wrap_shadow,
                (ordered_points[0][0], ordered_points[0][1]),
                (ordered_points[2][0], ordered_points[2][1]),
                color,
                3,
                8,
                0,
                0.05,
            )

            cv2.putText(
                img_wrap_shadow,
                f"L: {obj_l} cm",
                (x + 10, y + 50),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                color_text,
            )
            cv2.putText(
                img_wrap_shadow,
                f"W: {obj_w} cm",
                (x + 10, y + 65),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                color_text,
            )
    return img_wrap_shadow, obj_l, obj_w


def get_contours(
    img, c_thr=[20, 20], display=False, min_area=1000, filter=0, draw=False
):
    """
    Contours is a curve joining all the continuous points (along the boundary),
    having same color or intensity. The contours are a useful tool for shape analysis
    and object detection and recognition.

    .. note::
        For better accuracy, binary images are used. Input image is converted to gray
        scale, gaussian blur, canny edge detection. dilation and erosion are performed
        in the given order before finding contours using :find_contours:`cv2.findContours() <>`

        >>> CHAIN_APPROX_SIMPLE - to display few contour points
        >>> CHAIN_APPROX_NONE - to display all contour points

    Parameters
    ----------
    img : image
        Input image for contour extraction.
    c_thr : list, optional
        Threshold values for canny edge detection, by default [20, 20]
    display : bool, optional
        If, ``True`` displays canny edge detected image in a window,
        by default False
    min_area : int, optional
        Minimum area requirement for filtering contours,
        by default 1000
    filter : int, optional
        Value for filtering curve approximation (corner points), by default 0
    draw : bool, optional
        If ``True`` draw contour outlines on given input image, by default False

    Returns
    -------
    img
        Modified input image
    final_countours
        Filtered contour values from the input image which matches the ``min_area``
        and ``filter`` parameters.
    """
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_canny = cv2.Canny(img_blur, c_thr[0], c_thr[1])

    kernel = np.ones((3, 3))
    img_dila = cv2.dilate(img_canny, kernel, iterations=3)
    img_thrs = cv2.erode(img_dila, kernel, iterations=2)
    if display:
        cv2.imshow("medianCanny", img_thrs)

    contours, hiearchy = cv2.find_contours(
        img_thrs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    final_countours = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > min_area:
            perimeter = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * perimeter, True)
            bbox = cv2.boundingRect(approx)
            if filter > 0:
                if len(approx) == filter:
                    final_countours.append([len(approx), area, approx, bbox, i])
            else:
                final_countours.append([len(approx), area, approx, bbox, i])
    final_countours = sorted(final_countours, key=lambda x: x[1], reverse=True)
    if draw:
        for con in final_countours:
            cv2.drawContours(img, con[4], -1, (0, 0, 255), 3)
    return img, final_countours


def re_order(points):
    """Initially corner points are not in a particular order
    So it will not detect contours in any sequence.

    This function sorts the points in [top left , top right,
    bottom left, bottom right] using summation and subtraction method.

    Parameters
    ----------
    points : list, [[int,int],[int,int],[int,int],[int,int]]
        unsorted points in no given order

    Returns
    -------
    list, [[int,int],[int,int],[int,int],[int,int]]
        Sorted points in [top left , top right,
    bottom left, bottom right] order

    """
    points_new = np.zeros_like(points)
    points = points.reshape((4, 2))

    add = points.sum(1)
    points_new[0] = points[np.argmin(add)]
    points_new[3] = points[np.argmax(add)]

    diff = np.diff(points, axis=1)
    points_new[1] = points[np.argmin(diff)]
    points_new[2] = points[np.argmax(diff)]

    return points_new


def resize_image(scale, img):
    """
    Resizes a given image ie. either shrink or scale up to meet the size
    requirements.
    Parameters
    ----------
    scale : [float,float]
        The factor by which the image size has to be changed (% change).
        It is determined by the base height of the OAK cam from the objects
        on focus. Separate scale values for x and y axis is expected.
        Currently configured to 0.92 for both the axis. To modify the values
        refer to :class:`src.conf.config.CvDefaultConfig`.
    img :
        Image that needs to be resized.

    Returns
    -------
    imgage
        Returns a resized image by scale factor.
    """
    width = int(img.shape[1] * scale / 100)
    height = int(img.shape[0] * scale / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return img


# def empty(a):
#     pass


def relative_to_abs_path(relative_path):
    """Returns the absolute path for the provided relative path.

    .. note::
        To manage and dynamically create a hierarchical configuration by composition ``Hydra``
        is used. Hydra solves the problem of needing to specify a new output directory for each run,
        by creating a directory for each run and executing code within that working directory.

        To get the absolute path the folowing command is helpful,

        >>> hydra.utils.to_absolute_path(Path(relative_path)

    Parameters
    ----------
    relative_path :
        Relative path of a file

    Returns
    -------
        Returns absolute path for the given relative path
    """
    try:
        return str(hy.to_absolute_path(Path(relative_path)))
        # return str(os.path.abspath("../../" + relative_path))
    except FileNotFoundError:
        return None


def warp_img(img, points, w, h, pad=20):
    """Wraps a given image to the provided corner points

    Parameters
    ----------
    img : [type]
        [description]
    points : list, [[int,int],[int,int],[int,int],[int,int]]
        Four corner points to wrap the input image
    w : list, [int,int]
        Expected width of the final img
    h : list, [int,int]
        Expected height og the final img
    pad : int, optional
        Padding value to crop image to bring objects in focus.
        Elimates unwanted edge pixels, by default 20

    Returns
    -------
    img
        Wrapped image based on the provided corner points
    """
    points = re_order(points)

    p1 = np.float32(points)
    p2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(p1, p2)

    img_wrap = cv2.warpPerspective(img, matrix, (w, h))
    img_wrap = img_wrap[pad : img_wrap.shape[0] - pad, pad : img_wrap.shape[1] - pad]

    return img_wrap
