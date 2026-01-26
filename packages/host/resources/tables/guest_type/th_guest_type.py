#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('code', width='8em')
        r.fieldcell('description', width='100%')
        r.fieldcell('is_leader', width='10em', name='Leader')
        return struct

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='description', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top', datapath='.record')
        fb = top.formbuilder(cols=1, border_spacing='4px')
        fb.field('code', width='10em')
        fb.field('description', width='40em')
        fb.field('is_leader', width='10em', readonly=True)

    def th_options(self):
        return dict(dialog_height='200px', dialog_width='500px')
