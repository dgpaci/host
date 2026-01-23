#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Document Type lookup table (Identity Card, Passport, etc.)"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'document_type',
            pkey='id',
            name_long='Document Type',
            name_plural='Document Types',
            caption_field='description'
        )

        self.sysFields(tbl)

        tbl.column('code', size=':10', name_long='Code', validate_notnull=True, unique=True)
        tbl.column('description', size=':50', name_long='Description', validate_notnull=True)
