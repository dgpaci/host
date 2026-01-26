#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('name', width='30em')
        r.fieldcell('facility_type_description', width='15em', name='Type')
        r.fieldcell('comune_denominazione', width='20em', name='Municipality')
        return struct

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.borderContainer(region='top', datapath='.record', height='120px')
        fb = top.contentPane(region='center').formlet(cols=1, border_spacing='4px')
        fb.field('name')
        fb.field('facility_type_id', hasDownArrow=True)
        top.contentPane(region='right', width='400px').linkerBox('anagrafica_id',
                                                                 formResource='Form',
                                                                 dialog_windowRatio=.8)

        # Bottom section for related stays
        center = bc.tabContainer(region='center', margin='2px')
        stays_tab = center.contentPane(title='Stays')
        stays_tab.dialogTableHandler(relation='@stays',
                                     viewResource='ViewFromFacility',
                                     formResource='FormFromFacility')

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')
