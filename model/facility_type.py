#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Facility Type lookup table"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'facility_type',
            pkey='id',
            name_long='Facility Type',
            name_plural='Facility Types',
            caption_field='description'
        )

        self.sysFields(tbl)

        tbl.column('code', size=':10', name_long='Code', validate_notnull=True, unique=True)
        tbl.column('description', size=':50', name_long='Description', validate_notnull=True)
