#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Tourist Tax Rates lookup table"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'tourist_tax',
            pkey='id',
            name_long='Tourist Tax Rate',
            name_plural='Tourist Tax Rates',
            caption_field='description'
        )

        self.sysFields(tbl)

        tbl.column('code', size=':15', name_long='Code', validate_notnull=True, unique=True)
        tbl.column('description', size=':200', name_long='Description', validate_notnull=True)
        tbl.column('amount', dtype='N', size='12,2', name_long='Amount (EUR per night)', default=0,
                   name_short='Amount')
