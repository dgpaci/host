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
        self.taxInformations(bc.contentPane(region='top', height='60px', datapath='.record'))
        self.taxAmounts(bc.contentPane(region='center', margin='2px'))

    def taxInformations(self, pane):
        fb = pane.formlet(cols=3)
        fb.field('code')
        fb.field('description', colspan=2)

    def taxAmounts(self, pane):
        pane.dialogTableHandler(
            relation='@municipalities',
            viewResource='ViewMunicipalities',
            formResource='FormFromTax',
            addrow=False,
            delrow=False,
            pbl_classes=True
        )

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')
