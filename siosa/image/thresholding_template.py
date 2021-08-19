import cv2.cv2 as cv2

from siosa.common.decorations import override
from siosa.image.template import Template
from siosa.image.utils import threshold
from siosa.location.resolution import Resolution


class ThresholdingTemplate(Template):
    def __init__(self, template_name, template_file_path, resolution: Resolution):
        super().__init__(template_name, template_file_path, resolution)

    @override
    def process_image(self, image):
        return threshold(super().process_image(image))
