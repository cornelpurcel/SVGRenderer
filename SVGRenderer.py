import xml.etree.ElementTree as ET
from math import ceil
import cv2
import numpy as np


class SVGRenderer:
    MM_TO_PIXEL = 3.7795275591

    def __init__(self):
        self.elements = []
        self.outputFile = None
        self.width = None
        self.height = None
        self.units = None

    def load(self, filePath):
        tree = ET.parse(filePath)

        root = tree.getroot()
        ET.dump(root)
        self._initializeDimensions(root)

        # print(root.find(".//{http://www.w3.org/2000/svg}g"))
        for element in root.find(".//{http://www.w3.org/2000/svg}g"):
            self.elements.append(element)
            # ET.dump(element)

    def render(self):
        for element in self.elements:
            elementName = element.tag.split('}')[-1].lower()
            if elementName == "circle":
                self._drawCircle(**element.attrib)
            elif elementName == 'ellipse':
                self._drawEllipse(**element.attrib)
            elif elementName == 'square':
                self._drawSquare(**element.attrib)
            elif elementName == 'rect':
                self._drawRect(**element.attrib)
            elif elementName == 'line':
                self._drawLine(**element.attrib)
            elif elementName == 'polyline':
                self._drawPolyline(**element.attrib)

        cv2.imwrite("esketit.jpg", self.image)

    def _drawCircle(self, **params): ## TODO ADD STYLE SUPPORT
        print(params)
        cx, cy, r = float(params['cx']) * self.MM_TO_PIXEL, float(params['cy']) * self.MM_TO_PIXEL, float(params['r']) * self.MM_TO_PIXEL
        self.image = cv2.circle(self.image, (int(cx), int(cy)), int(r), (0, 0, 0), thickness=-1)

    def _drawSquare(self, **params): # TODO
        pass

    def _drawRect(self, **params): # TODO
        pass

    def _drawEllipse(self, **params): # TODO
        pass

    def _drawLine(self, **params): # TODO
        pass

    def _drawPolyline(self, **params): # TODO
        pass


    def _initializeDimensions(self, root):
        width = root.get("width")
        height = root.get("height")
        if width.endswith("mm"):
            self.width = ceil(int(width.strip('m')) * self.MM_TO_PIXEL)
            self.height = ceil(int(height.strip('m')) * self.MM_TO_PIXEL)
            self.units = "mm"
        else:
            try:
                self.width = ceil(int(width.strip()) * self.MM_TO_PIXEL)
                self.height = ceil(int(height.strip()) * self.MM_TO_PIXEL)
                self.units = "px"
            except:
                print("Nu s-au putut initializa dimensiunile")
                return None

        print("W: {}, H: {}".format(self.width, self.height))
        self.image = 255 * np.ones((self.height, self.width, 3), dtype=np.uint8)
        return self.width, self.height

