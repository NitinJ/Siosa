import logging
import time

import matplotlib.pyplot as plt
import numpy as np
from skimage.feature import match_template, peak_local_max


def plot(image, template, result, all_matches=None, name=''):
    if all_matches is None:
        all_matches = []

    res = np.unravel_index(np.argmax(result), result.shape)
    x, y = res[:2]
    res = np.unravel_index(np.argmin(result), result.shape)
    ymin, xmin = res[:2]
    template_width, template_height = template.shape[:2]

    fig = plt.figure('Debug', figsize=(12, 12), dpi=80)
    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4, sharex=ax3, sharey=ax3)

    # Template image
    ax1.imshow(template, cmap=plt.cm.gray)
    ax1.set_axis_off()
    ax1.set_title('template')

    # Top matched result
    ax2.imshow(image, cmap=plt.cm.gray)
    ax2.set_axis_off()
    ax2.set_title('image')
    ax2.add_patch(plt.Rectangle(
        (y - template_height // 2, x - template_width // 2), template_height,
        template_width, edgecolor='r', facecolor='none'))
    ax2.add_patch(plt.Rectangle(
        (ymin - template_height // 2, xmin - template_width // 2),
        template_height,
        template_width,
        edgecolor='g',
        facecolor='none'))

    # Result image
    ax3.imshow(result)
    ax3.set_axis_off()
    ax3.set_title('match_template - result')

    # All matches.
    ax4.imshow(image, cmap=plt.cm.gray)
    ax4.set_axis_off()
    ax4.set_title('match_template - all matches')
    for (y, x) in all_matches:
        ax4.add_patch(plt.Rectangle(
            (y - template_height // 2, x - template_width // 2),
            template_height,
            template_width,
            edgecolor='r',
            facecolor='none'))
    plt.show()


class ScikitTemplateMatcher:
    def __init__(self, threshold=0.80, debug=False):
        """
        Args:
            threshold:
            debug:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.debug = debug
        self.threshold = threshold

    def match_exists(self, image, template_image, name=''):
        ts1 = time.time()
        result = match_template(image, template_image)
        exists = result.max() > self.threshold
        self.logger.debug(
            "TemplateMatcher:{}, time: {}ms, exists: {}".format(
                name, int((time.time() - ts1) * 1000), exists))
        if self.debug:
            plot(image, template_image, result)
        return exists

    def match(self, image, template_image, name=''):
        ts1 = time.time()
        result = match_template(image, template_image, pad_input=True,
                                mode='edge')
        all_matches = self._find_all(result)
        if self.debug:
            plot(image, template_image, result, all_matches, name)
        peak_intensity = int(result.max() * 1000 ) / 1000
        self.logger.debug(
            "TemplateMatcher:{}, time: {}ms, npoints: {}, max_match: {}".format(
                name, int((time.time() - ts1) * 1000), len(all_matches),
                peak_intensity))
        return all_matches

    def _find_all(self, result):
        return [(r[1], r[0]) for r in peak_local_max(result, threshold_abs=self.threshold, exclude_border=2)]
