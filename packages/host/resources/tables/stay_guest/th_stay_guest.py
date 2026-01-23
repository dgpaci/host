#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('facility_name', width='20em', name='Facility')
        r.fieldcell('stay_check_in', width='10em', name='Check-in')
        r.fieldcell('stay_check_out', width='10em', name='Check-out')
        r.fieldcell('guest_name', width='25em', name='Guest')
        r.fieldcell('guest_type_description', width='15em', name='Type')
        r.fieldcell('tax_amount', width='100%', name='Tax', dtype='N')
        return struct

    def th_order(self):
        return 'stay_check_in DESC, guest_type_code'

    def th_query(self):
        return dict(column='guest_surname', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top', datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('stay_id', width='40em', colspan=2, hasDownArrow=True)
        fb.field('guest_id', width='40em', colspan=2,
                auxColumns='$birth_date,$citizenship',
                hasDownArrow=True)
        fb.field('guest_type_id', width='30em', hasDownArrow=True)
        fb.field('tourist_tax_id', width='40em', colspan=2, hasDownArrow=True)
        fb.field('tax_amount', width='15em', readonly=True)

    def th_options(self):
        return dict(dialog_height='350px', dialog_width='650px')
