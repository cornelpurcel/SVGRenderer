import xml.etree.ElementTree as ET
from math import ceil
from PIL import Image, ImageDraw


class SVGRenderer:
    MM_TO_PIXEL = 3.7795275591

    def __init__(self):
        self.elements = []
        self.outputFile = None
        self.width = None
        self.height = None
        self.units = None
        self.image = None

    def load(self, filePath):
        tree = ET.parse(filePath)

        root = tree.getroot()
        # ET.dump(root)
        self._initializeDimensions(root)

        # print(root.find(".//{http://www.w3.org/2000/svg}g"))
        for element in root.find(".//{http://www.w3.org/2000/svg}g"):
            self.elements.append(element)
            # ET.dump(element)

    def render(self):
        for element in self.elements:
            elementName = element.tag.split('}')[-1].lower()
            attributes = element.attrib
            style = {}
            if attributes.get('style', None):
                style = {pair.split(':')[0]: pair.split(':')[1] for pair in attributes['style'].split(";")}
                del attributes['style']
            if elementName == "circle":
                self._drawCircle(**attributes, **style)
            elif elementName == 'ellipse':
                self._drawEllipse(**attributes, **style)
            elif elementName == 'square':
                self._drawSquare(**attributes, **style)
            elif elementName == 'rect':
                self._drawRect(**attributes, **style)
            elif elementName == 'line':
                self._drawLine(**attributes, **style)
            elif elementName == 'polyline':
                self._drawPolyline(**attributes, **style)
        self.image.save("test.png")
        # self.image.show()

    def _drawCircle(self, **params):
        cx = self._convertToPixels(params['cx'])
        cy = self._convertToPixels(params['cy'])
        r = self._convertToPixels(params['r'])
        fillColor = self._getColorFromHex(params.get('fill', None))
        strokeColor = self._getColorFromHex(params.get("stroke", None))
        strokeWidth = self._convertToPixels(params.get("stroke-width", None))
        halfStrokeWidth = strokeWidth // 2
        opacity = self._opacityToAlpha(params.get("opacity", None))

        circleImage = Image.new("RGBA", self.image.size, None)
        drawContext = ImageDraw.Draw(circleImage)
        drawContext.ellipse([(cx - r - halfStrokeWidth, cy - r - halfStrokeWidth), (cx + r + halfStrokeWidth, cy + r + halfStrokeWidth)],
                            fill=(*strokeColor, opacity))
        drawContext.ellipse([(cx - r + halfStrokeWidth, cy - r + halfStrokeWidth), (cx + r - halfStrokeWidth, cy + r - halfStrokeWidth)],
                            fill=(*fillColor, opacity))

        self.image = Image.alpha_composite(self.image, circleImage)

    def _drawEllipse(self, **params):
        cx = self._convertToPixels(params['cx'])
        cy = self._convertToPixels(params['cy'])
        rx = self._convertToPixels(params['rx'])
        ry = self._convertToPixels(params['ry'])
        fillColor = self._getColorFromHex(params.get('fill', None))
        strokeColor = self._getColorFromHex(params.get("stroke", None))
        strokeWidth = self._convertToPixels(params.get("stroke-width", None))
        halfStrokeWidth = strokeWidth // 2
        opacity = self._opacityToAlpha(params.get("opacity", None))

        ellipseImage = Image.new("RGBA", self.image.size, None)
        drawContext = ImageDraw.Draw(ellipseImage)
        drawContext.ellipse([(cx - rx - halfStrokeWidth, cy - ry - halfStrokeWidth),
                             (cx + rx + halfStrokeWidth, cy + ry + halfStrokeWidth)],
                            fill=(*strokeColor, opacity))
        drawContext.ellipse([(cx - rx + halfStrokeWidth, cy - ry + halfStrokeWidth),
                             (cx + rx - halfStrokeWidth, cy + ry - halfStrokeWidth)],
                            fill=(*fillColor, opacity))

        self.image = Image.alpha_composite(self.image, ellipseImage)

    def _drawSquare(self, **params): # TODO
        pass

    def _drawRect(self, **params): # TODO
        pass

    def _drawLine(self, **params): # TODO
        pass

    def _drawPolyline(self, **params): # TODO
        pass

    def _convertToPixels(self, size):
        if not size:
            return 0
        size = float(size)
        if self.units == 'mm':
            return int(self.MM_TO_PIXEL * size)
        elif self.units == 'px':
            return int(size)

    def _getColorFromHex(self, hexColor):
        if hexColor is None:
            return 0, 0, 0
        hexColor = hexColor.strip('#')
        values = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                  '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}
        r, g, b = 0, 0, 0
        if len(hexColor) == 6:
            r = values[hexColor[0]] * 16 + values[hexColor[1]]
            g = values[hexColor[2]] * 16 + values[hexColor[3]]
            b = values[hexColor[4]] * 16 + values[hexColor[5]]
        # print ("RGB FOR {} IS {}".format(hexColor, (r, g, b)))
        return r, g, b

    def _opacityToAlpha(self, opacity):
        if opacity:
            return int(float(opacity) * 255)
        else:
            return 255

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
        self.image = Image.new("RGBA", (self.width, self.height), None)
        self.drawHandle = ImageDraw.Draw(self.image)
        return self.width, self.height

