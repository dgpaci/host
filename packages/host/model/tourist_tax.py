#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrdecorator import metadata

class Table(object):
    """Tourist Tax Rates lookup table"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'tourist_tax',
            pkey='code',
            name_long='!![en]Tourist Tax Rate',
            name_plural='!![en]Tourist Tax Rates',
            caption_field='description',
        )

        self.sysFields(tbl, id=False)

        tbl.column('code', size=':15', name_long='!![en]Code')
        tbl.column('description', size=':200', name_long='!![en]Description', validate_notnull=True)

    @metadata(mandatory=True)
    def sysRecord_MINOR_EX(self):
        return self.newrecord(code='0000000001',
                             description='Exemption for minors under 12 years')

    @metadata(mandatory=True)
    def sysRecord_RESIDENT_EX(self):
        return self.newrecord(code='0000000002',
                             description='Exemption for residents')

    @metadata(mandatory=True)
    def sysRecord_TOUR_GUIDE_EX(self):
        return self.newrecord(code='0000000003',
                             description='Exemption for tour guides (groups of 25+)')

    @metadata(mandatory=True)
    def sysRecord_STAFF_EX(self):
        return self.newrecord(code='0000000004',
                             description='Exemption for facility staff')

    @metadata(mandatory=True)
    def sysRecord_NO_EXEMPTION(self):
        return self.newrecord(code='0000000005',
                             description='NO EXEMPTION (standard rate)')

    @metadata(mandatory=True)
    def sysRecord_DISABILITY_EX(self):
        return self.newrecord(code='0000000006',
                             description='Exemption for non-self-sufficient persons with medical certificate')

    @metadata(mandatory=True)
    def sysRecord_CIVIL_PROT_EX(self):
        return self.newrecord(code='0000000007',
                             description='Exemption for Civil Protection volunteers')

    @metadata(mandatory=True)
    def sysRecord_MILITARY_EX(self):
        return self.newrecord(code='0000000008',
                             description='Exemption for police and military personnel on duty')

    @metadata(mandatory=True)
    def sysRecord_FREE_ACCOM_EX(self):
        return self.newrecord(code='0000000009',
                             description='Exemption for guests with free accommodation')
