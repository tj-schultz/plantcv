## Automatically Detect a Color Card

Automatically detects a color card and creates a labeled mask. 

**plantcv.transform.detect_color_card**(*rgb_img, label=None, \*\*kwargs*)

**returns** labeled_mask

- **Parameters**
    - rgb_img          - Input RGB image data containing a color card.
    - label            - Optional label parameter, modifies the variable name of observations recorded. (default = `pcv.params.sample_label`)
    - **kwargs         - Other keyword arguments passed to `cv2.adaptiveThreshold` and `cv2.circle`.
        - adaptive_method - Adaptive threhold method. 0 (mean) or 1 (Gaussian) (default = 1).
        - block_size      - Size of a pixel neighborhood that is used to calculate a threshold value (default = 51). We suggest using 127 if using `adaptive_method=0`.
        - radius         - Radius of circle to make the color card labeled mask (default = 20).
        - min_size         - Minimum chip size for filtering objects after edge detection (default = 1000)
- **Returns**
    - labeled_mask     - Labeled color card mask (useful downstream of this step in `pcv.transform.get_color_matrix` and `pcv.transform.correct_color`)
- **Example use:**
    - [Color Correction Tutorial](tutorials/transform_color_correction_tutorial.md)

!!! note
    Color chip size can only be used reasonably as a scaling factor (converting pixels to a known real world scale like cms)
    only when the color card is on a consistent plane relative to the subject AND the color card is parallel to the camera. 
    There are a few important assumptions that must be met in order to automatically detect color cards:
    
    - There is only one color card in the image.
    - Color card should be 4x6 (like an X-Rite ColorChecker Passport Photo). 

```python

from plantcv import plantcv as pcv
rgb_img, path, filename = pcv.readimage("target_img.png")
cc_mask = pcv.transform.detect_color_card(rgb_img=rgb_img)

avg_chip_size = pcv.outputs.observations['default']['median_color_chip_size']['value']
avg_chip_w = pcv.outputs.observations['default']['median_color_chip_width']['value']
avg_chip_h = pcv.outputs.observations['default']['median_color_chip_height']['value']

```

**Image automatically detected and masked**

![Screenshot](img/documentation_images/correct_color_imgs/detect_color_card.png)

**Source Code:** [Here](https://github.com/danforthcenter/plantcv/blob/main/plantcv/plantcv/transform/detect_color_card.py)