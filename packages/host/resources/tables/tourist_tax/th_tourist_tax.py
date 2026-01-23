#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('code', width='12em')
        r.fieldcell('description', width='100%')
        r.fieldcell('amount', width='10em', dtype='N')
        return struct

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='description', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top', datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('code', width='15em')
        fb.field('description', width='50em', colspan=2)
        fb.field('amount', width='15em')

    def th_options(self):
        return dict(dialog_height='250px', dialog_width='600px')
