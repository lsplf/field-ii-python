import image
import numpy as np
from quive import *
from language import *


class ImageWidget(Widget):
    gray_color_table = [qRgb(i, i, i) for i in range(256)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_color = Qt.white
        self.qim = QImage()

        self.short_cut = Shortcut('ctrl+w', self)
        self.short_cut.excited.connect(self.close)

        self.need_show = True
        self.path = ''

    @property
    def u_image(self) -> image.UImage:
        return self.attach(lambda: None)

    @u_image.setter
    def u_image(self, u_image: image.UImage):
        self.assign(u_image)

        im = u_image.pixel
        self.qim = QImage(im.flatten(), *im.T.shape, QImage.Format_Indexed8)

        w, h = im.T.shape
        self.qim.scaled(w * 2, h * 2)
        self.qim.setColorTable(self.gray_color_table)

        self.update()

    def update_u_image(self, u_image: image.UImage):
        self.u_image = u_image

    def paint(self, painter: Painter):
        font_size = language(47, 32)
        painter.setFont(QFont(language('SimSun', 'Times New Roman'), font_size))
        if self.u_image is None:
            return

        w, h = self.size
        text_size = (95 * font_size // 40, 45 * font_size // 40)
        text_width, text_height = text_size
        image_width, image_height = self.u_image.size

        expected_h = int(w / image_width * image_height)
        if expected_h > h:
            expected_w = int(h / image_height * image_width)
            painter.translate((w - expected_w) // 2, 0)
            w = expected_w
        else:
            painter.translate(0, (h - expected_h) // 2)
            h = expected_h

        painter.save()
        painter.translate(0, h)
        painter.rotate(-90)
        painter.drawText(QRect(0, 0, h, text_height), Qt.AlignCenter, language('深度 / mm', 'Axial distance (mm)'))
        painter.restore()
        w -= text_width
        h -= text_height * 2
        painter.translate(text_width, text_height / 3)

        half_image_width = image_width / 2
        for x in np.arange(0, half_image_width + 1e-5, 10):
            percent = (half_image_width + x) / image_width

            painter.drawLine(PointF(w * percent, h), PointF(w * percent, h+4))
            painter.draw_text_bottom(PointF(w * percent, h), "{}".format(int(x)),
                                     margin=5, background_color=Qt.transparent)

            if x == 0:
                painter.draw_text_bottom(PointF(w * percent, h), language("宽度 / mm", "Lateral distance (mm)"),
                                         margin=8 + text_height, background_color=Qt.transparent)
            else:
                percent = 1 - percent
                painter.drawLine(PointF(w * percent, h), PointF(w * percent, h+4))
                painter.draw_text_bottom(PointF(w * percent, h), "{}".format(-int(x)),
                                         margin=5, background_color=Qt.transparent)

        z_start = self.u_image.z_start
        for y in np.arange(0, image_height + 1e-5, 10):
            percent = y / image_height

            painter.drawLine(PointF(0, h * percent), PointF(-4, h * percent))
            painter.draw_text_left(PointF(0, h * percent), "{}".format(int(y + z_start)),
                                   margin=8, background_color=Qt.transparent)

        painter.drawLine(PointF(0, 0), PointF(0, h))
        painter.drawLine(PointF(0, 0), PointF(w, 0))

        painter.drawImage(QRect(0, 0, w, h), self.qim)
