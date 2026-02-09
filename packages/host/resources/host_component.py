#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class HostComponent(BaseComponent):

    @struct_method
    def styledBox(self, pane, title=None, color_variant=None, **kwargs):
        box = pane.div(_class=f'styledBox styledBox-{color_variant}', **kwargs)
        if title:
            box.div(title, _class=f'styledBoxTitle styledBoxTitle-{color_variant}')
        return box
