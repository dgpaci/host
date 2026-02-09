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


class ViewMunicipalities(BaseComponent):
    """View for municipalities in tourist tax form"""

    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('municipality_caption', width='30em', name='!![en]Municipality')
        r.fieldcell('amount', width='6em', edit=True)
        r.fieldcell('max_nights', width='6em', edit=True)

    def th_order(self):
        return 'municipality_caption'


class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')

        self.touristTaxInfo(bc.contentPane(region='top'))
        self.exemptionConditions(bc.contentPane(region='center', margin='5px'))
        
    def touristTaxInfo(self, pane):
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('tourist_tax_code', colspan=2, hasDownArrow=True)
        fb.field('comune_id', hasDownArrow=True)
        fb.field('localita')
        fb.field('amount', width='12em')
        fb.field('max_nights', width='12em')

    def exemptionConditions(self, pane):
        pane.bagGrid(title='!![en]Exemption Conditions',
                      datapath='.exemption_conditions',
                      struct=self._exemptionConditionsStruct,
                      margin='2px',
                      height='100%',
                      addrow=True,
                      delrow=True)

    def _exemptionConditionsStruct(self, struct):
        r = struct.view().rows()
        r.cell('column', name='!![en]Column', width='15em', edit=True,
              placeholder='!![en]Column name (e.g., age, citizenship)')
        r.cell('operator', name='!![en]Operator', width='8em', edit=True,
              values='<,>,<=,>=,==,!=',
              placeholder='!![en]Comparison operator')
        r.cell('value', name='!![en]Value', width='auto', edit=True,
              placeholder='!![en]Comparison value (can be fixed value or column reference with $)')
        return struct

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')


class FormFromTax(Form):
    
    def touristTaxInfo(self, pane):
        fb = pane.formlet(cols=2, border_spacing='4px')
        fb.field('amount', width='12em')
        fb.field('max_nights', width='12em')