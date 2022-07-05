# ROI functions

import os
import cv2
import numpy as np
from plantcv.plantcv._debug import _debug
from plantcv.plantcv import fatal_error
from plantcv.plantcv import params


# Create an ROI from a binary mask
def from_binary_image(img, bin_img):
    """
    Create an ROI from a binary image

    Inputs:
    img           = An RGB or grayscale image to plot the ROI on.
    bin_img       = Binary image to extract an ROI contour from.

    Outputs:
    roi_contour   = An ROI set of points (contour).
    roi_hierarchy = The hierarchy of ROI contour(s).

    :param img: numpy.ndarray
    :param bin_img: numpy.ndarray
    :return roi_contour: list
    :return roi_hierarchy: numpy.ndarray
    """
    # Make sure the input bin_img is binary
    if len(np.unique(bin_img)) != 2:
        fatal_error("Input image is not binary!")
    # Use the binary image to create an ROI contour
    roi_contour, roi_hierarchy = cv2.findContours(np.copy(bin_img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
    # Draw the ROI if requested
    _draw_roi(img=img, roi_contour=roi_contour)

    return roi_contour, roi_hierarchy


# Create a rectangular ROI
def rectangle(img, x, y, h, w):
    """
    Create a rectangular ROI.

    Inputs:
    img           = An RGB or grayscale image to plot the ROI on in debug mode.
    x             = The x-coordinate of the upper left corner of the rectangle.
    y             = The y-coordinate of the upper left corner of the rectangle.
    h             = The height of the rectangle.
    w             = The width of the rectangle.

    Outputs:
    roi_contour   = An ROI set of points (contour).
    roi_hierarchy = The hierarchy of ROI contour(s).

    :param img: numpy.ndarray
    :param x: int
    :param y: int
    :param h: int
    :param w: int
    :return roi_contour: list
    :return roi_hierarchy: numpy.ndarray
    """
    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]

    # Create the rectangle contour vertices
    pt1 = [x, y]
    pt2 = [x, y + h - 1]
    pt3 = [x + w - 1, y + h - 1]
    pt4 = [x + w - 1, y]

    # Create the ROI contour
    roi_contour = [np.array([[pt1], [pt2], [pt3], [pt4]], dtype=np.int32)]
    roi_hierarchy = np.array([[[-1, -1, -1, -1]]], dtype=np.int32)

    # Draw the ROI if requested
    _draw_roi(img=img, roi_contour=roi_contour)

    # Check whether the ROI is correctly bounded inside the image
    if x < 0 or y < 0 or x + w > width or y + h > height:
        fatal_error("The ROI extends outside of the image!")

    return roi_contour, roi_hierarchy


# Create a circular ROI
def circle(img, x, y, r):
    """
    Create a circular ROI.

    Inputs:
    img           = An RGB or grayscale image to plot the ROI on in debug mode.
    x             = The x-coordinate of the center of the circle.
    y             = The y-coordinate of the center of the circle.
    r             = The radius of the circle.

    Outputs:
    roi_contour   = An ROI set of points (contour).
    roi_hierarchy = The hierarchy of ROI contour(s).

    :param img: numpy.ndarray
    :param x: int
    :param y: int
    :param r: int
    :return roi_contour: list
    :return roi_hierarchy: numpy.ndarray
    """
    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]

    # Initialize a binary image of the circle
    bin_img = np.zeros((height, width), dtype=np.uint8)
    # Draw the circle on the binary image
    cv2.circle(bin_img, (x, y), r, 255, -1)

    # Use the binary image to create an ROI contour
    roi_contour, roi_hierarchy = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]

    # Draw the ROI if requested
    _draw_roi(img=img, roi_contour=roi_contour)

    # Check whether the ROI is correctly bounded inside the image
    if x - r < 0 or x + r > width or y - r < 0 or y + r > height:
        fatal_error("The ROI extends outside of the image!")

    return roi_contour, roi_hierarchy


# Create an elliptical ROI
def ellipse(img, x, y, r1, r2, angle):
    """
    Create an elliptical ROI.

    Inputs:
    img           = An RGB or grayscale image to plot the ROI on in debug mode.
    x             = The x-coordinate of the center of the ellipse.
    y             = The y-coordinate of the center of the ellipse.
    r1            = The radius of the minor axis.
    r2            = The radius of the major axis.
    angle         = The angle of rotation in degrees of the major axis.

    Outputs:
    roi_contour   = An ROI set of points (contour).
    roi_hierarchy = The hierarchy of ROI contour(s).

    :param img: numpy.ndarray
    :param x: int
    :param y: int
    :param r1: int
    :param r2: int
    :param angle: double
    :return roi_contour: list
    :return roi_hierarchy: numpy.ndarray
    """
    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]

    # Initialize a binary image of the ellipse
    bin_img = np.zeros((height, width), dtype=np.uint8)
    # Draw the ellipse on the binary image
    cv2.ellipse(bin_img, (x, y), (r1, r2), angle, 0, 360, 255, -1)

    # Use the binary image to create an ROI contour
    roi_contour, roi_hierarchy = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]

    # Draw the ROI if requested
    _draw_roi(img=img, roi_contour=roi_contour)

    # Checks ellipse goes outside the image by checking row and column sum of edges
    if (np.sum(bin_img[0, :]) + np.sum(bin_img[-1, :]) + np.sum(bin_img[:, 0]) + np.sum(bin_img[:, -1]) > 0) or \
            len(roi_contour) == 0:
        fatal_error("The ROI extends outside of the image, or ROI is not on the image!")

    return roi_contour, roi_hierarchy


# Draw the ROI on a reference image
def _draw_roi(img, roi_contour):
    """
    Draw an ROI
    :param img: numpy.ndarray
    :param roi_contour: list
    """
    # Make a copy of the reference image
    ref_img = np.copy(img)
    # If the reference image is grayscale convert it to color
    if len(np.shape(ref_img)) == 2:
        ref_img = cv2.cvtColor(ref_img, cv2.COLOR_GRAY2BGR)
    # Draw the contour on the reference image
    cv2.drawContours(ref_img, roi_contour, -1, (255, 0, 0), params.line_thickness)
    _debug(visual=ref_img,
           filename=os.path.join(params.debug_outdir, str(params.device) + "_roi.png"))
    
from dataclasses import dataclass
@dataclass
class Objects:
    """Class for keeping track of an item in inventory."""
    contours: list
    hierarchy: np.ndarray

    def save(self, filename):
        np.savez(filename, contours = self.contours, hierarchy = self.hierarchy)
    @staticmethod
    def load(filename):
        file = np.load(filename)
        obj = Objects(file['contours'].tolist(),file['hierarchy'])
        return obj
    
def _calculate_grid(bin_mask, nrows, ncols):
    from sklearn.mixture import GaussianMixture
    contours, hierarchy = cv2.findContours(bin_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
    centers = []
    for c in contours:
        m = cv2.moments(c)
        cmx, cmy = (float(m['m10'] / m['m00']), float(m['m01'] / m['m00']))
        centers.append((cmx,cmy))
    #cluster by x and y coordinates to get grid layout
    centers_x = np.array(np.array([i[0] for i in centers]).reshape(-1,1))
    centers_y = np.array(np.array([i[1] for i in centers]).reshape(-1,1))
    gm_x = GaussianMixture(n_components=ncols, random_state=0).fit(centers_x)
    gm_y = GaussianMixture(n_components=nrows, random_state=0).fit(centers_y)
    clusters_x = np.sort(gm_x.means_[:,0])
    clusters_y = np.sort(gm_y.means_[:,0])
    spacing_x = (clusters_x[ncols-1] - clusters_x[0])/(ncols-1)if ncols > 1 else 0
    spacing_y = (clusters_y[nrows-1] - clusters_y[0])/(nrows-1) if nrows > 1 else 0
    spacing = (round(spacing_x), round(spacing_y))
    coord = (round(clusters_x[0]),round(clusters_y[0]))
    return coord, spacing

def _adjust_radius_coord(height, width, coord, radius):
    x = [i[0] for i in coord]
    y = [i[1] for i in coord]
    return _adjust_radius_max_min(height, width, radius, max(x),min(x),max(y),min(y))
    
def _adjust_radius_grid(height, width, coord, radius, spacing, nrows, ncols):
    xmax = coord[0] + (ncols-1)*spacing[0]
    xmin = coord[0]
    ymax = coord[1] + (nrows-1)*spacing[1]
    ymin = coord[1]
    return _adjust_radius_max_min(height,width,radius,xmax,xmin,ymax,ymin)

def _adjust_radius_max_min(height, width, radius, xmax, xmin, ymax, ymin):
    if ((xmin < 0) or (xmax > width) or (ymin < 0) or (ymax > height)):
        fatal_error("An ROI extends outside of the image!")
    distances_to_edge = [xmin, width-xmax, ymin, height-ymax]
    min_distance = min(distances_to_edge)
    if min_distance < radius:
        print('Shrinking radius to make ROIs fit in the image')
        radius = min_distance - 1
    return(radius)
    
def _rois_from_coordinates(img, coord=None, radius=None):
    if radius is None:
        fatal_error("Specify a radius if creating rois from a list of coordinates")
    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]
    radius = _adjust_radius_coord(height, width, coord, radius)
    overlap_img = np.zeros((height, width))
    # Initialize a binary image of the circle that will contain all ROI
    all_roi_img = np.zeros((height, width), dtype=np.uint8)
    roi_contour = []
    roi_hierarchy = []
    for i in range(0, len(coord)):
    # Initialize a binary image for each circle
        bin_img = np.zeros((height, width), dtype=np.uint8)
        y = coord[i][1]
        x = coord[i][0]
        # Draw the circle on the binary image
        # Keep track of all roi
        all_roi_img = cv2.circle(all_roi_img, (x, y), radius, 255, -1)
        # Keep track of each roi individually to check overlapping
        circle_img = cv2.circle(bin_img, (x, y), radius, 255, -1)
        overlap_img = overlap_img + circle_img
        # Make a list of contours and hierarchies
        rc, rh = cv2.findContours(circle_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
        roi_contour.append(rc)
        roi_hierarchy.append(rh)
    return roi_contour, roi_hierarchy, overlap_img, all_roi_img

def _grid_roi(img, nrows, ncols, coord=None, radius=None, spacing=None):
    if radius is None:
        if spacing[0] == 0:
            radius = round(0.325*spacing[1])
        elif spacing[1] == 0:
            radius = round(0.325*spacing[0])
        else:
            radius = round(0.325*(spacing[0]+spacing[1])/2)
    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]
    radius = _adjust_radius_grid(height, width, coord, radius, spacing, nrows, ncols)
    overlap_img = np.zeros((height, width))
    # Initialize a binary image of the circle that will contain all ROI
    all_roi_img = np.zeros((height, width), dtype=np.uint8)
    roi_contour = []
    roi_hierarchy = []
    # Loop over each row
    for i in range(0, nrows):
        # The upper left corner is the y starting coordinate + the ROI offset * the vertical spacing
        y = coord[1] + i * spacing[1]
        # Loop over each column
        for j in range(0, ncols):
            # Initialize a binary image for each circle
            bin_img = np.zeros((height, width), dtype=np.uint8)
            # The upper left corner is the x starting coordinate + the ROI offset * the
            # horizontal spacing between chips
            x = coord[0] + j * spacing[0]
            # Draw the circle on the binary images
            # Keep track of all roi
            all_roi_img = cv2.circle(all_roi_img, (x, y), radius, 255, -1)
            # Keep track of each roi individually to check overlapping
            circle_img = cv2.circle(bin_img, (x, y), radius, 255, -1)
            overlap_img = overlap_img + circle_img
            # Make a list of contours and hierarchies
            rc, rh = cv2.findContours(circle_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
            roi_contour.append(rc)
            roi_hierarchy.append(rh)
    return roi_contour, roi_hierarchy, overlap_img, all_roi_img

def auto_grid(bin_mask, nrows, ncols, radius=None, img=None):
    """
    Detect and create multiple circular ROIs on a single binary mask
    Inputs
    bin_mask      = A binary mask.
    nrows         = Number of rows in ROI layout. 
    ncols         = Number of columns in ROI layout.    
    radius        = Optional parameter to specify the radius of the circular rois.
    img           = (Optional) Image from which the binary mask was derived.
     
    Returns:
    roi_objects   = a dataclass with roi objects and hierarchies
    :param bin_mask: numpy.ndarray
    :param nrows: int
    :param ncols: int
    :param radius: int
    :param img: numpy.ndarray
    :return roi_objects: plantcv.roi.Objects
    """
    coord, spacing = _calculate_grid(bin_mask, nrows, ncols)
    if img is None:
        img = bin_mask
    roi_contour, roi_hierarchy, overlap_img, all_roi_img = _grid_roi(img, nrows, ncols,
                                                                     coord, radius, spacing)
    if np.amax(overlap_img) > 255:
        print("WARNING: Two or more of the user defined regions of interest overlap! "
              "If you only see one ROI then they may overlap exactly.")
    # Draw the ROIs if requested
    # Create an array of contours and list of hierarchy for debug image
    roi_contour1, _ = cv2.findContours(all_roi_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
    _draw_roi(img=img, roi_contour=roi_contour1)
    roi_objects = Objects(roi_contour, roi_hierarchy)
    return roi_objects
    
def multi(img, coord, radius=None, spacing=None, nrows=None, ncols=None):
    """
    Create multiple circular ROIs on a single image
    Inputs
    img           = Input image data.
    coord         = Two-element tuple of the center of the top left object (x,y) or a list of tuples identifying
                    the center of each roi [(x1,y1),(x2,y2)]
    radius        = A single radius for all ROIs.
    spacing       = Two-element tuple of the horizontal and vertical spacing between ROIs, (x,y). Ignored if `coord`
                    is a list and `rows` and `cols` are None.
    nrows         = Number of rows in ROI layout. Should be missing or None if each center coordinate pair is listed.
    ncols         = Number of columns in ROI layout. Should be missing or None if each center coordinate pair is listed.
    Returns:
    roi_objects   = a dataclass with roi objects and hierarchies
    :param img: numpy.ndarray
    :param coord: tuple, list
    :param radius: int
    :param spacing: tuple
    :param nrows: int
    :param ncols: int
    :return roi_objects: plantcv.roi.Objects
    """
    # Grid of ROIs
    if (type(coord) == tuple) and ((nrows and ncols) is not None) and (type(spacing) == tuple):
        roi_contour, roi_hierarchy, overlap_img, all_roi_img = _grid_roi(img, nrows, ncols, coord,
                                                                         radius, spacing)   
        # User specified ROI centers
    elif (type(coord) == list) and ((nrows and ncols) is None) and (spacing is None):
        roi_contour, roi_hierarchy, overlap_img, all_roi_img = _rois_from_coordinates(img=img, coord=coord,
                                                                                           radius=radius)
    else:
        fatal_error("Function can either make a grid of ROIs (user must provide nrows, ncols, spacing, and coord) "
                    "or take custom ROI coordinates (user must provide only a list of tuples to 'coord' parameter). "
                    "For automatic detection of a grid layout from just nrows, ncols, and a binary mask, use auto_grid")
        

    if np.amax(overlap_img) > 255:
        print("WARNING: Two or more of the user defined regions of interest overlap! "
              "If you only see one ROI then they may overlap exactly.")

    # Draw the ROIs if requested
    # Create an array of contours and list of hierarchy for debug image
    roi_contour1, _ = cv2.findContours(all_roi_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
    _draw_roi(img=img, roi_contour=roi_contour1)
    roi_objects = Objects(roi_contour, roi_hierarchy)
    return roi_objects

def custom(img, vertices):
    """
    Create an custom polygon ROI.

        Inputs:
        img           = An RGB or grayscale image to plot the ROI on in debug mode.
        vertices      = List of vertices of the desired polygon ROI

        Outputs:
        roi_contour   = An ROI set of points (contour).
        roi_hierarchy = The hierarchy of ROI contour(s).

        :param img: numpy.ndarray
        :param vertices: list
        :return roi_contour: list
        :return roi_hierarchy: numpy.ndarray
    """
    # Get the height and width of the reference image
    height, width = np.shape(img)[:2]

    roi_contour = [np.array(vertices, dtype=np.int32)]
    roi_hierarchy = np.array([[[-1, -1, -1, -1]]], dtype=np.int32)

    # Draw the ROIs if requested
    _draw_roi(img=img, roi_contour=roi_contour)

    # Check that the ROI doesn't go off the screen
    for i in vertices:
        (x, y) = i
        if x < 0 or x > width or y < 0 or y > height:
            fatal_error("An ROI extends outside of the image!")

    return roi_contour, roi_hierarchy
