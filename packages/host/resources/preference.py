#!/usr/bin/env python
# encoding: utf-8

class AppPref(object):

    def prefpane_host(self, parent, **kwargs):
        pane = parent.contentPane(**kwargs)
        fb = pane.formbuilder()
        fb.dbSelect(value='^.tourist_tax_default_code',
                   lbl='!![en]Default Tourist Tax Code',
                   dbtable='host.tourist_tax',
                   width='30em',
                   hasDownArrow=True)
