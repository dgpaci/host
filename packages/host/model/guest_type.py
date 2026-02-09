#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrdecorator import metadata

class Table(object):
    """Guest Type lookup table (Tipo Alloggiato)"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'guest_type',
            pkey='code',
            name_long='!![en]Guest Type',
            name_plural='!![en]Guest Types',
            caption_field='description',
            lookup=True
        )

        self.sysFields(tbl, id=False)

        tbl.column('code', size=':2', name_long='!![en]Code')
        tbl.column('description', size=':50', name_long='!![en]Description', validate_notnull=True)
        tbl.column('is_leader', dtype='B', name_long='!![en]Is Group Leader')


    @metadata(mandatory=True)
    def sysRecord_SINGLE_GUEST(self):
        return self.newrecord(code='16',
                             description='OSPITE SINGOLO')

    @metadata(mandatory=True)
    def sysRecord_FAMILY_HEAD(self):
        return self.newrecord(code='17',
                             description='CAPO FAMIGLIA', 
                             is_leader=True)

    @metadata(mandatory=True)
    def sysRecord_GROUP_HEAD(self):
        return self.newrecord(code='18',
                             description='CAPO GRUPPO', 
                             is_leader=True)

    @metadata(mandatory=True)
    def sysRecord_FAMILY_MEMBER(self):
        return self.newrecord(code='19',
                             description='FAMILIARE')

    @metadata(mandatory=True)
    def sysRecord_GROUP_MEMBER(self):
        return self.newrecord(code='20',
                             description='MEMBRO GRUPPO')
