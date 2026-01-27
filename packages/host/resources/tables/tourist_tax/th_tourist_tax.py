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
        bc = form.center.borderContainer()

        # Top section - basic info
        top = bc.contentPane(region='top', height='80px', datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('code', width='15em')
        fb.field('description', width='50em', colspan=2)

        # Center section - amounts per municipality (baggrid)
        center = bc.contentPane(region='center', margin='2px')
        center.div('!![en]Amounts per Municipality', font_weight='bold', margin_bottom='5px')
        center.bagGrid(
            storepath='.record.amounts',
            struct=self._bagGridStruct,
            addrow=True,
            delrow=True
        )

    def _bagGridStruct(self, struct):
        """Define baggrid structure for amounts per municipality"""
        r = struct.view().rows()
        r.cell('comune_id', name='!![en]Municipality', width='30em',
              dtype='L', size='22',
              dbtable='glbl.comune',
              validate_notnull=True)
        r.cell('amount', name='!![en]Amount (EUR)', width='15em',
              dtype='N', format='#,###.00',
              validate_notnull=True)

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')
