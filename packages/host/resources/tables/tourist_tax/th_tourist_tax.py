#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('code', width='12em')
        r.fieldcell('description', width='100%')
        return struct

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='description', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        self.taxInformations(bc.contentPane(region='top', height='60px'))
        self.taxAmounts(bc.contentPane(region='center', margin='2px'))
    
    def taxInformations(self, pane):
        fb = pane.formlet(cols=3)
        fb.field('code')
        fb.field('description', colspan=2)
        
    def taxAmounts(self, pane):
        pane.bagGrid(
            title='!![en]Amounts per Municipality',
            storepath='.amounts',
            struct=self._bagGridStruct,
            addrow=True,
            delrow=True,
            height='100%'
        )

    def _bagGridStruct(self, struct):
        """Define baggrid structure for amounts per municipality"""
        r = struct.view().rows()
        r.cell('comune_id', name='!![en]Municipality', width='30em',
              dtype='L', size='22',
              table='glbl.comune',
              edit=True,
              validate_notnull=True)
        r.cell('amount', name='!![en]Amount (EUR)', width='15em',
              dtype='N', format='#,###.00',
              edit=True,
              validate_notnull=True)

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')
