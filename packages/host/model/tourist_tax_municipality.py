#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Tourist Tax Municipality - amounts per municipality/locality"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'tourist_tax_municipality',
            pkey='id',
            name_long='!![en]Tourist Tax Municipality',
            name_plural='!![en]Tourist Tax Municipalities',
            caption_field='municipality_caption'
        )

        self.sysFields(tbl)

        tbl.column('tourist_tax_code', size=':15', name_long='!![en]Tourist Tax', validate_notnull=True)\
            .relation('host.tourist_tax.code', mode='foreignkey',
                     relation_name='municipalities', onDelete='cascade')

        tbl.column('comune_id', size='22', name_long='!![en]Municipality')\
            .relation('glbl.comune.id', mode='foreignkey',
                     relation_name='tourist_tax_municipalities', onDelete='setnull')

        tbl.column('localita', size=':100', name_long='!![en]Locality')

        tbl.column('amount', dtype='N', size='12,2', name_long='!![en]Amount (EUR)',
                   name_short='!![en]Amount', default=0, validate_notnull=True)

        tbl.column('max_nights', dtype='I', name_long='!![en]Maximum Nights',
                   name_short='!![en]Max Nights',
                   tip='!![en]Maximum number of consecutive nights for which the tax applies. Leave empty for no limit.')

        tbl.column('exemption_conditions', dtype='X', name_long='!![en]Exemption Conditions',
                   tip='!![en]Bag containing exemption rules: column, operator, and value for this municipality')

        tbl.aliasColumn('comune_denominazione', '@comune_id.denominazione',
                       name_long='!![en]Municipality Name')

        tbl.formulaColumn('municipality_caption',
                         'COALESCE($comune_denominazione, $localita)',
                         name_long='!![en]Municipality Caption')

        # Unique constraint: one row per tourist_tax + (comune_id OR localita)
        tbl.column('municipality_key', size=':100', name_long='!![en]Municipality Key',
                   indexed=True, unique=True)

    def trigger_onInserting(self, record=None, **kwargs):
        """Set municipality key for uniqueness"""
        self._set_municipality_key(record)

    def trigger_onUpdating(self, record=None, old_record=None, **kwargs):
        """Update municipality key"""
        self._set_municipality_key(record)
        
    def _set_municipality_key(self, record):
        """Set municipality_key based on comune_id or localita"""
        tourist_tax_code = record.get('tourist_tax_code', '')
        comune_id = record.get('comune_id', '')
        localita = record.get('localita', '')

        if comune_id:
            record['municipality_key'] = f"{tourist_tax_code}_{comune_id}"
        elif localita:
            record['municipality_key'] = f"{tourist_tax_code}_{localita.upper()}"
        else:
            raise Exception("Either comune_id or localita must be provided")