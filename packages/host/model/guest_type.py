#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Guest Type lookup table (Tipo Alloggiato)"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'guest_type',
            pkey='id',
            name_long='Guest Type',
            name_plural='Guest Types',
            caption_field='description'
        )

        self.sysFields(tbl)

        tbl.column('code', size=':2', name_long='Code', validate_notnull=True, unique=True)
        tbl.column('description', size=':50', name_long='Description', validate_notnull=True)

        # Helper columns to identify group leaders
        tbl.formulaColumn('is_leader',
                         "$code IN ('17', '18')",
                         dtype='B',
                         name_long='Is Group Leader')
