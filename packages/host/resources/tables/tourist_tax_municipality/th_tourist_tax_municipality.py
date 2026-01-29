#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('tourist_tax_code')
        r.fieldcell('comune_id')
        r.fieldcell('localita')
        r.fieldcell('amount', width='6em')
        r.fieldcell('max_nights', width='6em')
    
    
class Form(BaseComponent):
    def th_form(self, form):
        fb = form.record.formbuilder(cols=2)
        fb.field('tourist_tax_code')
        fb.field('comune_id')
        fb.field('localita')
        fb.field('amount')
        fb.field('max_nights')


class ViewMunicipalities(BaseComponent):
    """View for municipalities in tourist tax form"""

    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('municipality_caption', width='30em', name='!![en]Municipality')
        r.fieldcell('amount', width='6em', edit=True)
        r.fieldcell('max_nights', width='6em', edit=True)

    def th_order(self):
        return 'municipality_caption'
