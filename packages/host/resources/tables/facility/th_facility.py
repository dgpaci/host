#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('name', width='30em')
        r.fieldcell('facility_type_description', width='15em', name='Type')
        r.fieldcell('comune_nome', width='20em', name='Municipality')
        r.fieldcell('owner_name', width='100%', name='Owner')
        return struct

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top', datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('name', width='40em', colspan=2)
        fb.field('anagrafica_id', width='40em', colspan=2)
        fb.field('facility_type_id', width='30em')
        fb.field('comune_id', width='30em', hasDownArrow=True)

        # Bottom section for related stays
        center = bc.tabContainer(region='center', margin='2px')
        stays_tab = center.contentPane(title='Stays')
        stays_tab.dialogTableHandler(relation='@stays',
                                     viewResource='ViewFromFacility')

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')

class ViewFromFacility(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('check_in_date', width='10em', name='Check-in')
        r.fieldcell('check_out_date', width='10em', name='Check-out')
        r.fieldcell('nights', width='8em')
        return struct

    def th_order(self):
        return 'check_in_date DESC'
