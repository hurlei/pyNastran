"""
The preferences menu handles:
 - Font Size
 - Background Color
 - Text Color
 - Annotation Color
 - Annotation Size
 - Clipping Min
 - Clipping Max
"""
from __future__ import print_function
from math import log10, ceil

from qtpy import QtGui
from qtpy.QtWidgets import (
    QLabel, QPushButton, QGridLayout, QApplication, QHBoxLayout, QVBoxLayout,
    QSpinBox, QDoubleSpinBox, QColorDialog, QLineEdit, QCheckBox, QComboBox)
import vtk

from pyNastran.gui.utils.qt.pydialog import PyDialog
from pyNastran.gui.utils.qt.qpush_button_color import QPushButtonColor
from pyNastran.gui.menus.menu_utils import eval_float_from_string


class PreferencesWindow(PyDialog):
    """
    +-------------+
    | Preferences |
    +---------------------------------+
    | Text Size        ______ Default |
    | Annotation Color ______         |
    | Annotation Size  ______         |
    | Picker Size      ______         |
    | Back Color       ______         |
    | Text Color       ______         |
    |                                 |
    |        Apply OK Cancel          |
    +---------------------------------+
    """
    def __init__(self, data, win_parent=None):
        """
        Saves the data members from data and
        performs type checks
        """
        PyDialog.__init__(self, data, win_parent)

        self._updated_preference = False

        self._default_font_size = data['font_size']
        self._default_text_size = 14
        self._default_annotation_size = 18
        self._default_coord_scale = 0.05 * 100.
        self._default_coord_text_scale = 0.5 * 100.
        self._default_clipping_min = data['min_clip']
        self._default_clipping_max = data['max_clip']
        #self._default_annotation_size = data['annotation_size'] # int
        #self.default_magnify = data['magnify']

        self.dim_max = data['dim_max']
        self._use_gradient_background = data['use_gradient_background'] # bool
        self._show_corner_coord = data['show_corner_coord']
        self._annotation_size = data['annotation_size'] # int

        #self.out_data = data
        self._picker_size = data['picker_size'] * 100.
        self._coord_scale = data['coord_scale'] * 100.
        self._coord_text_scale = data['coord_text_scale'] * 100.
        self._magnify = data['magnify']
        self._text_size = data['text_size']

        self.annotation_color_float, self.annotation_color_int = _check_color(
            data['annotation_color'])
        self.background_color_float, self.background_color_int = _check_color(
            data['background_color'])
        self.background_color2_float, self.background_color2_int = _check_color(
            data['background_color2'])
        self.text_color_float, self.text_color_int = _check_color(
            data['text_color'])

        self.setWindowTitle('Preferences')
        self.create_widgets()
        self.create_layout()
        self.set_connections()
        self.on_font(self._default_font_size)
        self.on_gradient_scale()
        #self.show()

    def create_widgets(self):
        """creates the display window"""
        # Text Size
        self.font_size_label = QLabel("Font Size:")
        self.font_size_edit = QSpinBox(self)
        self.font_size_edit.setValue(self._default_font_size)
        self.font_size_edit.setRange(7, 20)
        self.font_size_button = QPushButton("Default")

        #-----------------------------------------------------------------------
        # Annotation Color
        self.annotation_color_label = QLabel("Annotation Color:")
        self.annotation_color_edit = QPushButtonColor(self.annotation_color_int)
        self.annotation_color_label.hide()
        self.annotation_color_edit.hide()
        #-----------------------------------------------------------------------
        # Text Color
        self.text_size_label = QLabel("Text Size:")
        self.text_size_edit = QSpinBox(self)
        self.text_size_edit.setValue(self._default_text_size)
        self.text_size_edit.setRange(7, 30)
        self.text_size_button = QPushButton("Default")

        # Text Color
        self.text_color_label = QLabel("Text Color:")
        self.text_color_edit = QPushButtonColor(self.text_color_int)

        #-----------------------------------------------------------------------
        # Background Color
        self.background_color_label = QLabel("Btm Background Color:")
        self.background_color_edit = QPushButtonColor(self.background_color_int)

        # Background Color2
        self.gradient_scale_label = QLabel("Gradient Background:")
        self.gradient_scale_checkbox = QCheckBox()
        self.gradient_scale_checkbox.setChecked(self._use_gradient_background)

        self.background_color2_label = QLabel("Top Background Color:")
        self.background_color2_edit = QPushButtonColor(self.background_color2_int)

        #-----------------------------------------------------------------------
        # Annotation Size
        self.annotation_size_label = QLabel("Annotation Size:")
        self.annotation_size_edit = QSpinBox(self)
        self.annotation_size_edit.setRange(1, 500)
        self.annotation_size_edit.setValue(self._annotation_size)
        self.annotation_size_button = QPushButton("Default")

        #-----------------------------------------------------------------------
        # Picker Size
        self.picker_size_label = QLabel("Picker Size (% of Screen):")
        self.picker_size_edit = QDoubleSpinBox(self)
        self.picker_size_edit.setRange(0., 10.)

        log_dim = log10(self.dim_max)
        decimals = int(ceil(abs(log_dim)))

        decimals = max(6, decimals)
        self.picker_size_edit.setDecimals(decimals)
        self.picker_size_edit.setSingleStep(10. / 5000.)
        self.picker_size_edit.setValue(self._picker_size)

        #-----------------------------------------------------------------------
        # Clipping Min
        self.clipping_min_label = QLabel("Clipping Min:")
        self.clipping_min_edit = QLineEdit(str(self._default_clipping_min))
        self.clipping_min_button = QPushButton("Default")

        # Clipping Max
        self.clipping_max_label = QLabel("Clipping Max:")
        self.clipping_max_edit = QLineEdit(str(self._default_clipping_max))
        self.clipping_max_button = QPushButton("Default")

        #-----------------------------------------------------------------------
        self.coord_scale_label = QLabel('Coordinate System Scale:')
        self.coord_scale_button = QPushButton("Default")

        self.coord_scale_edit = QDoubleSpinBox(self)
        self.coord_scale_edit.setRange(0.1, 100.)
        self.coord_scale_edit.setDecimals(3)
        self.coord_scale_edit.setSingleStep(2.5)
        self.coord_scale_edit.setValue(self._coord_scale)

        self.coord_text_scale_label = QLabel('Coordinate System Text Scale:')
        self.coord_text_scale_button = QPushButton("Default")

        self.coord_text_scale_edit = QDoubleSpinBox(self)
        self.coord_text_scale_edit.setRange(0.1, 200.)
        self.coord_text_scale_edit.setDecimals(3)
        self.coord_text_scale_edit.setSingleStep(2.5)
        self.coord_text_scale_edit.setValue(self._coord_text_scale)

        # Show corner coord
        self.corner_coord_label = QLabel("Show Corner Coordinate System:")
        self.corner_coord_checkbox = QCheckBox()
        self.corner_coord_checkbox.setChecked(self._show_corner_coord)

        #-----------------------------------------------------------------------
        self.magnify_label = QLabel('Screenshot Magnify:')
        self.magnify_edit = QSpinBox(self)
        self.magnify_edit.setMinimum(1)
        self.magnify_edit.setMaximum(10)
        self.magnify_edit.setValue(self._magnify)

        #-----------------------------------------------------------------------
        # closing
        self.apply_button = QPushButton("Apply")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

    #def create_legend_widgets(self):
        #"""
        #Creates the widgets for the legend control

        #Name    Itailic  Bold     Font
        #====    =======  =====  ========
        #Title    check   check  pulldown
        #Label    check   check  pulldown
        #"""
        #self.name_label = QLabel("Name:")
        #self.italic_label = QLabel("Italic:")
        #self.bold_label = QLabel("Bold:")
        #self.font_label = QLabel("Font:")
        #self.legend_label = QLabel("Legend:")

        #self.legend_title_name = QLabel("Title")
        #self.legend_title_italic_check = QCheckBox()
        #self.legend_title_bold_check = QCheckBox()
        #self.legend_title_font_edit = QComboBox()
        #self.legend_title_font_edit.addItems(['cat', 'dog', 'frog'])

        #self.legend_label_italic_name = QLabel("Label")
        #self.legend_label_italic_check = QCheckBox()
        #self.legend_label_bold_check = QCheckBox()
        #self.legend_label_font_edit = QComboBox()
        #self.legend_label_font_edit.addItems(['cat2', 'dog2', 'frog2'])

    #def create_legend_layout(self):
        #"""
        #Creates the layout for the legend control

        #Name    Itailic  Bold     Font
        #====    =======  =====  ========
        #Title    check   check  pulldown
        #Label    check   check  pulldown
        #"""
        #grid2 = QGridLayout()
        #grid2.addWidget(self.legend_label, 0, 0)

        #grid2.addWidget(self.name_label, 1, 0)
        #grid2.addWidget(self.italic_label, 1, 1)
        #grid2.addWidget(self.bold_label, 1, 2)
        #grid2.addWidget(self.font_label, 1, 3)

        #grid2.addWidget(self.legend_title_name, 2, 0)
        #grid2.addWidget(self.legend_title_italic_check, 2, 1)
        #grid2.addWidget(self.legend_title_bold_check, 2, 2)
        #grid2.addWidget(self.legend_title_font_edit, 2, 3)

        #grid2.addWidget(self.legend_label_italic_name, 3, 0)
        #grid2.addWidget(self.legend_label_italic_check, 3, 1)
        #grid2.addWidget(self.legend_label_bold_check, 3, 2)
        #grid2.addWidget(self.legend_label_font_edit, 3, 3)
        #return grid2

    def create_layout(self):
        grid = QGridLayout()

        irow = 0
        grid.addWidget(self.font_size_label, irow, 0)
        grid.addWidget(self.font_size_edit, irow, 1)
        grid.addWidget(self.font_size_button, irow, 2)
        irow += 1

        grid.addWidget(self.gradient_scale_label, irow, 0)
        grid.addWidget(self.gradient_scale_checkbox, irow, 1)
        irow += 1

        grid.addWidget(self.background_color2_label, irow, 0)
        grid.addWidget(self.background_color2_edit, irow, 1)
        irow += 1

        grid.addWidget(self.background_color_label, irow, 0)
        grid.addWidget(self.background_color_edit, irow, 1)
        irow += 1

        grid.addWidget(self.text_color_label, irow, 0)
        grid.addWidget(self.text_color_edit, irow, 1)
        irow += 1

        grid.addWidget(self.text_size_label, irow, 0)
        grid.addWidget(self.text_size_edit, irow, 1)
        grid.addWidget(self.text_size_button, irow, 2)
        irow += 1

        grid.addWidget(self.annotation_color_label, irow, 0)
        grid.addWidget(self.annotation_color_edit, irow, 1)
        irow += 1

        grid.addWidget(self.annotation_size_label, irow, 0)
        grid.addWidget(self.annotation_size_edit, irow, 1)
        grid.addWidget(self.annotation_size_button, irow, 2)
        irow += 1

        #grid.addWidget(self.clipping_min_label, irow, 0)
        #grid.addWidget(self.clipping_min_edit, irow, 1)
        #grid.addWidget(self.clipping_min_button, irow, 2)
        #irow += 1

        #grid.addWidget(self.clipping_max_label, irow, 0)
        #grid.addWidget(self.clipping_max_edit, irow, 1)
        #grid.addWidget(self.clipping_max_button, irow, 2)
        #irow += 1

        grid.addWidget(self.corner_coord_label, irow, 0)
        grid.addWidget(self.corner_coord_checkbox, irow, 1)
        irow += 1

        grid.addWidget(self.coord_scale_label, irow, 0)
        grid.addWidget(self.coord_scale_edit, irow, 1)
        grid.addWidget(self.coord_scale_button, irow, 2)
        irow += 1

        grid.addWidget(self.coord_text_scale_label, irow, 0)
        grid.addWidget(self.coord_text_scale_edit, irow, 1)
        grid.addWidget(self.coord_text_scale_button, irow, 2)
        irow += 1

        #-----------------------------------------------
        grid.addWidget(self.magnify_label, irow, 0)
        grid.addWidget(self.magnify_edit, irow, 1)
        irow += 1

        grid.addWidget(self.picker_size_label, irow, 0)
        grid.addWidget(self.picker_size_edit, irow, 1)
        irow += 1

        #self.create_legend_widgets()
        #grid2 = self.create_legend_layout()
        ok_cancel_box = QHBoxLayout()
        ok_cancel_box.addWidget(self.apply_button)
        ok_cancel_box.addWidget(self.ok_button)
        ok_cancel_box.addWidget(self.cancel_button)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        #vbox.addStretch()
        #vbox.addLayout(grid2)
        vbox.addStretch()

        vbox.addLayout(ok_cancel_box)
        self.setLayout(vbox)

    def set_connections(self):
        self.font_size_button.clicked.connect(self.on_default_font_size)
        self.font_size_edit.valueChanged.connect(self.on_font)

        self.annotation_size_edit.editingFinished.connect(self.on_annotation_size)
        self.annotation_size_edit.valueChanged.connect(self.on_annotation_size)
        self.annotation_color_edit.clicked.connect(self.on_annotation_color)
        self.annotation_size_button.clicked.connect(self.on_default_annotation_size)

        self.background_color_edit.clicked.connect(self.on_background_color)
        self.background_color2_edit.clicked.connect(self.on_background_color2)
        self.gradient_scale_checkbox.clicked.connect(self.on_gradient_scale)

        self.text_color_edit.clicked.connect(self.on_text_color)
        self.text_size_edit.valueChanged.connect(self.on_text_size)
        self.text_size_button.clicked.connect(self.on_default_text_size)

        self.picker_size_edit.valueChanged.connect(self.on_picker_size)
        self.picker_size_edit.editingFinished.connect(self.on_picker_size)

        self.coord_scale_edit.valueChanged.connect(self.on_coord_scale)
        self.coord_scale_edit.editingFinished.connect(self.on_coord_scale)
        self.coord_scale_button.clicked.connect(self.on_default_coord_scale)
        self.corner_coord_checkbox.clicked.connect(self.on_corner_coord)

        self.coord_text_scale_edit.valueChanged.connect(self.on_coord_text_scale)
        self.coord_text_scale_edit.editingFinished.connect(self.on_coord_text_scale)
        self.coord_text_scale_button.clicked.connect(self.on_default_coord_text_scale)

        self.magnify_edit.valueChanged.connect(self.on_magnify)
        self.magnify_edit.editingFinished.connect(self.on_magnify)

        self.clipping_min_button.clicked.connect(self.on_default_clipping_min)
        self.clipping_max_button.clicked.connect(self.on_default_clipping_max)

        self.apply_button.clicked.connect(self.on_apply)
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.on_cancel)
        # closeEvent

    def on_font(self, value=None):
        """update the font for the current window"""
        if value is None:
            value = self.font_size_edit.value()
        font = QtGui.QFont()
        font.setPointSize(value)
        self.setFont(font)

    def on_annotation_size(self, value=None):
        """update the annotation size"""
        if value is None:
            value = int(self.annotation_size_edit.text())
        self._annotation_size = value
        #self.on_apply(force=True)
        #self.min_edit.setText(str(self._default_min))
        #self.min_edit.setStyleSheet("QLineEdit{background: white;}")
        self.update_annotation_size_color()

    def update_annotation_size_color(self):
        if self.win_parent is not None:
            self.win_parent.settings.set_annotation_size_color(size=self._annotation_size)

    def on_gradient_scale(self):
        is_checked = self.gradient_scale_checkbox.isChecked()
        self.background_color2_label.setEnabled(is_checked)
        self.background_color2_edit.setEnabled(is_checked)
        if self.win_parent is not None:
            self.win_parent.settings.set_gradient_background(use_gradient_background=is_checked)

    def on_corner_coord(self):
        is_checked = self.corner_coord_checkbox.isChecked()
        if self.win_parent is not None:
            self.win_parent.set_corner_axis_visiblity(is_checked, render=True)

    def on_annotation_color(self):
        rgb_color_ints = self.annotation_color_int
        title = "Choose an annotation color"
        passed, rgb_color_ints, rgb_color_floats = self.on_color(
            self.annotation_color_edit, rgb_color_ints, title)
        if passed:
            self.annotation_color_int = rgb_color_ints
            self.annotation_color_float = rgb_color_floats
            self.update_annotation_size_color()

    def on_background_color(self):
        """ Choose a background color"""
        title = "Choose a primary background color"
        rgb_color_ints = self.background_color_int
        color_edit = self.background_color_edit
        func_name = 'set_background_color'
        passed, rgb_color_ints, rgb_color_floats = self._background_color(
            title, color_edit, rgb_color_ints, func_name)
        if passed:
            self.background_color_int = rgb_color_ints
            self.background_color_float = rgb_color_floats

    def on_background_color2(self):
        """ Choose a background color"""
        title = "Choose a secondary background color"
        rgb_color_ints = self.background_color2_int
        color_edit = self.background_color2_edit
        func_name = 'set_background_color2'
        passed, rgb_color_ints, rgb_color_floats = self._background_color(
            title, color_edit, rgb_color_ints, func_name)
        if passed:
            self.background_color2_int = rgb_color_ints
            self.background_color2_float = rgb_color_floats

    def _background_color(self, title, color_edit, rgb_color_ints, func_name):
        """helper method for ``on_background_color`` and ``on_background_color2``"""
        passed, rgb_color_ints, rgb_color_floats = self.on_color(
            color_edit, rgb_color_ints, title)
        if passed:
            if self.win_parent is not None:
                settings = self.win_parent.settings
                func_background_color = getattr(settings, func_name)
                func_background_color(rgb_color_floats)
        return passed, rgb_color_ints, rgb_color_floats

    def on_text_color(self):
        """ Choose a text color """
        rgb_color_ints = self.text_color_int
        title = "Choose a text color"
        passed, rgb_color_ints, rgb_color_floats = self.on_color(
            self.text_color_edit, rgb_color_ints, title)
        if passed:
            self.text_color_int = rgb_color_ints
            self.text_color_float = rgb_color_floats
            if self.win_parent is not None:
                self.win_parent.settings.set_text_color(rgb_color_floats)

    def on_default_text_size(self):
        self.text_size_edit.setValue(self._default_text_size)
        self.on_text_size(self._default_text_size)

    def on_text_size(self, value=None):
        if value is None:
            value = self.text_size_edit.value()
        self._text_size = value
        if self.win_parent is not None:
            self.win_parent.settings.set_text_size(value)

    def on_color(self, color_edit, rgb_color_ints, title):
        """pops a color dialog"""
        col = QColorDialog.getColor(QtGui.QColor(*rgb_color_ints), self,
                                    title)
        if not col.isValid():
            return False, rgb_color_ints, None

        color_float = col.getRgbF()[:3]  # floats
        color_int = [int(colori * 255) for colori in color_float]

        assert isinstance(color_float[0], float), color_float
        assert isinstance(color_int[0], int), color_int

        color_edit.setStyleSheet(
            "QPushButton {"
            "background-color: rgb(%s, %s, %s);" % tuple(color_int) +
            #"border:1px solid rgb(255, 170, 255); "
            "}")
        return True, color_int, color_float

    def on_picker_size(self):
        self._picker_size = float(self.picker_size_edit.text())
        if self.win_parent is not None:
            self.win_parent.element_picker_size = self._picker_size / 100.
        #self.on_apply(force=True)

    def on_magnify(self, value=None):
        if value is None:
            value = self.magnify_edit.value()
        self._magnify = value
        if self.win_parent is not None:
            self.win_parent.settings.set_magnify(value)

    #---------------------------------------------------------------------------
    def on_coord_scale(self, value=None):
        if value is None:
            value = self.coord_scale_edit.value()
        self._coord_scale = value
        if self.win_parent is not None:
            self.win_parent.settings.set_coord_scale(value / 100.)

    def on_default_coord_scale(self):
        self.coord_scale_edit.setValue(self._default_coord_scale)
        self.on_coord_scale(self._default_coord_scale)

    def on_coord_text_scale(self, value=None):
        if value is None:
            value = self.coord_text_scale_edit.value()
        self._coord_text_scale = value
        if self.win_parent is not None:
            self.win_parent.settings.set_coord_text_scale(value / 100.)

    def on_default_coord_text_scale(self):
        self.coord_text_scale_edit.setValue(self._default_coord_text_scale)
        self.on_coord_text_scale(self._default_coord_text_scale)

    #---------------------------------------------------------------------------
    def on_default_font_size(self):
        self.font_size_edit.setValue(self._default_font_size)
        self.on_font(self._default_font_size)

    def on_default_annotation_size(self):
        self.annotation_size_edit.setValue(self._default_annotation_size)
        self.on_annotation_size(self._default_annotation_size)

    def on_default_clipping_min(self):
        self.clipping_min_edit.setText(str(self._default_clipping_min))
        self.clipping_min_edit.setStyleSheet("QLineEdit{background: white;}")

    def on_default_clipping_max(self):
        self.clipping_max_edit.setText(str(self._default_clipping_max))
        self.clipping_max_edit.setStyleSheet("QLineEdit{background: white;}")

    def on_validate(self):
        font_size_value, flag0 = check_float(self.font_size_edit)
        annotation_size_value, flag1 = check_float(self.annotation_size_edit)
        assert isinstance(self.annotation_color_float[0], float), self.annotation_color_float
        assert isinstance(self.annotation_color_int[0], int), self.annotation_color_int
        picker_size_value, flag2 = check_float(self.picker_size_edit)

        clipping_min_value, flag3 = check_label_float(self.clipping_min_edit)
        clipping_max_value, flag4 = check_label_float(self.clipping_max_edit)

        if all([flag0, flag1, flag2, flag3, flag4]):
            self._annotation_size = annotation_size_value
            self._picker_size = picker_size_value

            self.out_data['font_size'] = int(font_size_value)
            self.out_data['min_clip'] = min(clipping_min_value, clipping_max_value)
            self.out_data['max_clip'] = max(clipping_min_value, clipping_max_value)
            self.out_data['clicked_ok'] = True
            return True
        return False

    def on_apply(self, force=False):
        passed = self.on_validate()

        if (passed or force) and self.win_parent is not None:
            self.win_parent.settings.on_set_font_size(self.out_data['font_size'])

            #self.win_parent.settings.set_annotation_size_color(self._annotation_size)
            #self.win_parent.element_picker_size = self._picker_size / 100.
        if passed and self.win_parent is not None:
            self.win_parent.clipping_obj.apply_clipping(self.out_data)
        return passed

    def on_ok(self):
        passed = self.on_apply()
        if passed:
            self.close()
            #self.destroy()

    def on_cancel(self):
        self.out_data['close'] = True
        self.close()


def check_float(cell):
    text = cell.text()
    value = float(text)
    return value, True

def check_label_float(cell):
    text = cell.text()
    try:
        value = eval_float_from_string(text)
        cell.setStyleSheet("QLineEdit{background: white;}")
        return value, True
    except ValueError:
        cell.setStyleSheet("QLineEdit{background: red;}")
        return None, False

def _check_color(color_float):
    assert len(color_float) == 3, color_float
    assert isinstance(color_float[0], float), color_float
    color_int = [int(colori * 255) for colori in color_float]
    return color_float, color_int

def main():
    # kills the program when you hit Cntl+C from the command line
    # doesn't save the current state as presumably there's been an error
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


    import sys
    # Someone is launching this directly
    # Create the QApplication
    app = QApplication(sys.argv)
    #The Main window
    data = {
        'font_size' : 8,
        'use_gradient_background' : True,
        'background_color' : (0., 0., 0.), # black
        'background_color2' : (1., 0., 1.), # purple
        'coord_scale' : 0.05,
        'coord_text_scale' : 1.0,
        'show_corner_coord' : False,
        'magnify' : 5,

        'text_size' : 12,
        'text_color' : (0., 1., 0.), # green

        'annotation_color' : (1., 0., 0.), # red
        'annotation_size' : 11,
        'picker_size' : 10.,

        'min_clip' : 0.,
        'max_clip' : 10,

        'dim_max' : 502.,

    }
    main_window = PreferencesWindow(data)
    main_window.show()
    # Enter the main loop
    app.exec_()

if __name__ == "__main__":
    main()