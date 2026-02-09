#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrdecorator import metadata

class Table(object):
    """Facility Type lookup table"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'facility_type',
            pkey='code',
            name_long='!![en]Facility Type',
            name_plural='!![en]Facility Types',
            caption_field='description',
            lookup=True
        )

        self.sysFields(tbl, id=False)

        tbl.column('code', size=':10', name_long='!![en]Code')
        tbl.column('description', size=':50', name_long='!![en]Description', validate_notnull=True)

    @metadata(mandatory=True)
    def sysRecord_HOTEL(self):
        return self.newrecord(code='HOTEL', description='Hotel')

    @metadata(mandatory=True)
    def sysRecord_BB(self):
        return self.newrecord(code='BB', description='Bed & Breakfast')

    @metadata(mandatory=True)
    def sysRecord_APART(self):
        return self.newrecord(code='APART', description='Apartment')

    @metadata(mandatory=True)
    def sysRecord_AGRITU(self):
        return self.newrecord(code='AGRITU', description='Agriturismo')

    @metadata(mandatory=True)
    def sysRecord_HOSTEL(self):
        return self.newrecord(code='HOSTEL', description='Hostel')

    @metadata(mandatory=True)
    def sysRecord_VILLA(self):
        return self.newrecord(code='VILLA', description='Villa')

    @metadata(mandatory=True)
    def sysRecord_CAMPING(self):
        return self.newrecord(code='CAMPING', description='Camping')
