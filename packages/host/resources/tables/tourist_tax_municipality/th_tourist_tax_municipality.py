#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class ViewMunicipalities(BaseComponent):
    """View for municipalities in tourist tax form"""

    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('municipality_caption', width='30em', name='!![en]Municipality')
        r.fieldcell('amount', width='15em', edit=True)
        return struct

    def th_order(self):
        return 'municipality_caption'
