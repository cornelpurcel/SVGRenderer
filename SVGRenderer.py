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
            elif elementName == 'rect':
                self._drawRect(**attributes, **style)
            elif elementName == 'line':
                self._drawLine(**attributes, **style)
            elif elementName == 'polyline':
                self._drawPolyline(**attributes, **style)
            elif elementName == 'path':
                self._drawPath(**attributes, **style)
        self.image.save("test.png")
        self.image.show()

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
        drawContext.ellipse([(cx - r - halfStrokeWidth, cy - r - halfStrokeWidth),
                             (cx + r + halfStrokeWidth, cy + r + halfStrokeWidth)],
                            fill=(*strokeColor, opacity))
        drawContext.ellipse([(cx - r + halfStrokeWidth, cy - r + halfStrokeWidth),
                             (cx + r - halfStrokeWidth, cy + r - halfStrokeWidth)],
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

    def _drawRect(self, **params):
        x = self._convertToPixels(params['x'])
        y = self._convertToPixels(params['y'])
        height = self._convertToPixels(params['height'])
        width = self._convertToPixels(params['width'])
        fillColor = self._getColorFromHex(params.get('fill', None))
        strokeColor = self._getColorFromHex(params.get("stroke", None))
        strokeWidth = self._convertToPixels(params.get("stroke-width", None))
        halfStrokeWidth = strokeWidth // 2
        opacity = self._opacityToAlpha(params.get("opacity", None))

        rectImage = Image.new("RGBA", self.image.size, None)
        drawContext = ImageDraw.Draw(rectImage)

        drawContext.rectangle(
            [(x - halfStrokeWidth, y - halfStrokeWidth), (x + width + halfStrokeWidth, y + height + halfStrokeWidth)],
            fill=(*strokeColor, opacity))
        drawContext.rectangle(
            [(x + halfStrokeWidth, y + halfStrokeWidth), (x + width - halfStrokeWidth, y + height - halfStrokeWidth)],
            fill=(*fillColor, opacity))

        self.image = Image.alpha_composite(self.image, rectImage)


    def _drawLine(self, **params):
        x1 = self._convertToPixels(params['x1'])
        y1 = self._convertToPixels(params['y1'])
        x2 = self._convertToPixels(params['x2'])
        y2 = self._convertToPixels(params['y2'])
        strokeColor = self._getColorFromHex(params.get("stroke", None))
        strokeWidth = self._convertToPixels(params.get("stroke-width", None))
        opacity = self._opacityToAlpha(params.get("opacity", None))

        lineImage = Image.new("RGBA", self.image.size, None)
        drawContext = ImageDraw.Draw(lineImage)
        drawContext.line([(x1, y1), (x2, y2)], fill=(*strokeColor, opacity), width=strokeWidth)

        self.image = Image.alpha_composite(self.image, lineImage)

    def _drawPolyline(self, **params): # TODO
        strokeColor = self._getColorFromHex(params.get("stroke", None))
        strokeWidth = self._convertToPixels(params.get("stroke-width", None))
        opacity = self._opacityToAlpha(params.get("opacity", None))

        points = params.get("points", None)
        if not points:
            return
        polylineImage = Image.new("RGBA", self.image.size, None)
        drawContext = ImageDraw.Draw(polylineImage)
        points = points.split()
        lastPoint = self._getPoints(points[0])
        for index in range(1, len(points)):
            currentPoint = self._getPoints(points[index])
            drawContext.line([lastPoint, currentPoint], fill=(*strokeColor, opacity), width = strokeWidth)
            lastPoint = currentPoint

        self.image = Image.alpha_composite(self.image, polylineImage)


    def _drawPath(self, **params):
        strokeColor = self._getColorFromHex(params.get("stroke", None))
        strokeWidth = self._convertToPixels(params.get("stroke-width", None))
        opacity = self._opacityToAlpha(params.get("opacity", None))

        def drawBezier(points, drawContext, width, fill):
            xu, yu, u = 0.0, 0.0, 0.0
            lastPoint = points[0]
            while u <= 1:
                xu = (1 - u) ** 3 * points[0][0] + 3 * u * (1 - u) ** 2 * points[1][0] + \
                     3 * (1 - u) * u ** 2 * points[2][0] + u ** 3 * points[3][0]
                yu = (1 - u) ** 3 * points[0][1] + 3 * u * (1 - u) ** 2 * points[1][1] + \
                     3 * (1 - u) * u ** 2 * points[2][1] + u ** 3 * points[3][1]
                drawContext.line([lastPoint, (int(xu), int(yu))], width=width, fill=fill)
                lastPoint = (int(xu), int(yu))
                u += 0.001

        operations = ('m', 'M', 'C', 'c', 'z')
        pathImage = Image.new("RGBA", self.image.size, None)
        drawContext = ImageDraw.Draw(pathImage)
        tokens = params['d'].split()
        index = 0
        lastPoint = (0, 0)
        firstPoint = (0, 0)
        lastOperation = ''
        while index < len(tokens):
            print("Checking ", tokens[index])
            if tokens[index] in ('z', 'Z'):
                drawContext.line([lastPoint, firstPoint], width=strokeWidth, fill=(*strokeColor, opacity))
                break
            elif tokens[index] == "M" or (tokens[index] not in operations and lastOperation == 'M'):
                if tokens[index] not in operations:
                    index -= 1
                newPoint = self._getPoints(tokens[index + 1])
                if index != 0:
                    drawContext.line([lastPoint, newPoint], width=strokeWidth, fill=(*strokeColor, opacity))
                else:
                    firstPoint = newPoint
                lastPoint = newPoint
                lastOperation = 'M'
                index += 2
            elif tokens[index] == "m" or (tokens[index] not in operations and lastOperation == 'm'):
                if tokens[index] not in operations:
                    index -= 1
                diffPoint = self._getPoints(tokens[index+1])
                newPoint = lastPoint[0] + diffPoint[0], lastPoint[1] + diffPoint[1]
                if index != 0:
                    drawContext.line([lastPoint, newPoint], width=strokeWidth, fill=(*strokeColor, opacity))
                else:
                    firstPoint = newPoint
                lastPoint = newPoint
                lastOperation = 'm'
                index += 2
            elif tokens[index] == "c" or (tokens[index] not in operations and lastOperation == 'c'):
                if tokens[index] not in operations:
                    index -= 1
                diffPoint = self._getPoints(tokens[index + 1])
                point1 = lastPoint[0] + diffPoint[0], lastPoint[1] + diffPoint[1]
                diffPoint = self._getPoints(tokens[index + 2])
                point2 = lastPoint[0] + diffPoint[0], lastPoint[1] + diffPoint[1]
                diffPoint = self._getPoints(tokens[index + 3])
                point3 = lastPoint[0] + diffPoint[0], lastPoint[1] + diffPoint[1]
                drawBezier([lastPoint, point1, point2, point3], drawContext, width=strokeWidth, fill=(*strokeColor, opacity))
                lastPoint = point3
                lastOperation = 'c'
                index += 4
            else:
                index += 1
        self.image = Image.alpha_composite(self.image, pathImage)

    def _getPoints(self, text):
        points = text.split(',')
        return self._convertToPixels(points[0]), self._convertToPixels(points[1])

    def _convertToPixels(self, size):
        if not size:
            return 0
        try:
            size = float(size)
        except ValueError:
            if size.endswith("mm"):
                return int(self.MM_TO_PIXEL * float(size[:-2]))
            elif size.endswith('px'):
                return int(float(size[:-2]))
        if self.units == 'mm':
            return int(self.MM_TO_PIXEL * size)
        elif self.units == 'px':
            return int(size)

    def _getColorFromHex(self, hexColor):
        if hexColor is None:
            return 0, 0, 0
        if hexColor.startswith("rgb"):
            hexColor = hexColor[4:-1].split(',')
            if len(hexColor) != 3:
                return 0, 0, 0
            return int(hexColor[0]), int(hexColor[1]), int(hexColor[2])
        elif hexColor.startswith("#"):
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

