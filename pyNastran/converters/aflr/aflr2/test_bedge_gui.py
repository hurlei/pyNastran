from __future__ import print_function
import os
import warnings
import unittest

import numpy as np

import pyNastran
from pyNastran.converters.aflr.aflr2.aflr2 import read_bedge
from pyNastran.converters.aflr.aflr2.bedge_io import BEdge_IO
from pyNastran.gui.testing_methods import FakeGUIMethods
from pyNastran.utils.log import get_logger

warnings.simplefilter('always')
np.seterr(all='raise')

PKG_PATH = pyNastran.__path__[0]
MODEL_PATH = os.path.join(PKG_PATH, 'converters', 'aflr', 'aflr2')


class BEdge_GUI(BEdge_IO, FakeGUIMethods):
    def __init__(self):
        FakeGUIMethods.__init__(self)
        BEdge_IO.__init__(self)


class TestBEdgeGUI(unittest.TestCase):
    def test_bedge_geometry(self):
        """tests the bedge gui"""
        bedge_filename = os.path.join(MODEL_PATH, 'm3.bedge')

        test = BEdge_GUI()
        test.log = get_logger(log=None, level='warning', encoding='utf-8')
        test.load_bedge_geometry(bedge_filename)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()