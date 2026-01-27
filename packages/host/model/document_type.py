#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrdecorator import metadata

class Table(object):
    """Document Type lookup table (Identity Card, Passport, etc.)"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'document_type',
            pkey='code',
            name_long='!![en]Document Type',
            name_plural='!![en]Document Types',
            caption_field='description',
            lookup=True
        )

        self.sysFields(tbl, id=False)

        tbl.column('code', size=':10', name_long='!![en]Code')
        tbl.column('description', size=':50', name_long='!![en]Description', validate_notnull=True)

    @metadata(mandatory=True)
    def sysRecord_IDENT(self):
        return self.newrecord(code='IDENT', description="CARTA DI IDENTITA'")

    @metadata(mandatory=True)
    def sysRecord_IDELE(self):
        return self.newrecord(code='IDELE', description="CARTA IDENTITA' ELETTRONICA")

    @metadata(mandatory=True)
    def sysRecord_PASOR(self):
        return self.newrecord(code='PASOR', description='PASSAPORTO ORDINARIO')

    @metadata(mandatory=True)
    def sysRecord_PATEN(self):
        return self.newrecord(code='PATEN', description='PATENTE DI GUIDA')

    @metadata(mandatory=True)
    def sysRecord_CIDIP(self):
        return self.newrecord(code='CIDIP', description='CARTA ID. DIPLOMATICA')
