#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Document Type lookup table (Identity Card, Passport, etc.)"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'document_type',
            pkey='code',
            name_long='Document Type',
            name_plural='Document Types',
            caption_field='description',
            lookup=True
        )

        self.sysFields(tbl, id=False)

        tbl.column('code', size=':10', name_long='Code')
        tbl.column('description', size=':50', name_long='Description', validate_notnull=True)
