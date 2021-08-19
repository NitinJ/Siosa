import numpy as np

from siosa.common.decorations import override
from siosa.image.template import Template
from siosa.image.utils import threshold, grayscale
from siosa.location.resolution import Resolution


class TradeCurrencyTemplate(Template):
    def __init__(self, template_name, template_file_path, resolution: Resolution):
        super().__init__(template_name, template_file_path, resolution)

    @override
    def process_image(self, image):
        image = threshold(image)

        # Remove the green channel from the image to remove the green
        # hazy border when trade has been accepted by the other player.
        image[:, :, 1] = np.zeros([image.shape[0], image.shape[1]])
        # return image
        return grayscale(image)
