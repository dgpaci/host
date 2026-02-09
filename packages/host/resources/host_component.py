#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class HostComponent(BaseComponent):

    @struct_method
    def styledBox(self, pane, title=None, color_variant=None, linkerBar=None, **kwargs):
        """
        Create a styled box with optional title and linker dbSelect.

        Args:
            title: Box title text
            color_variant: Color variant (blue, green, orange, yellow, purple)
            linkerBar: Dict with dbSelect attributes to add next to title
                      Example: linkerBar=dict(table='host.guest',
                                             value='^#FORM.pkey',
                                             condition='$stay_id=:stay_id',
                                             condition_stay_id='=#FORM.record.stay_id',
                                             lbl='Guests',
                                             width='15em')

        Returns:
            The styled box div element
        """
        box = pane.div(_class=f'styledBox styledBox-{color_variant}', **kwargs)

        if title or linkerBar:
            title_bar = box.div(_class='styledBoxTitleBar')
            if title:
                title_bar.div(title, _class=f'styledBoxTitle styledBoxTitle-{color_variant}')
            if linkerBar:
                title_bar.dbSelect(**linkerBar)

        return box
