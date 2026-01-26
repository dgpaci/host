#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Accommodation Facility table"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'facility',
            pkey='id',
            name_long='Facility',
            name_plural='Facilities',
            caption_field='name'
        )

        self.sysFields(tbl)

        tbl.column('anagrafica_id', size='22', name_long='Owner/Manager', validate_notnull=True)\
            .relation('er_core.anagrafica.id', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')

        tbl.column('name', size=':100', name_long='Facility Name', validate_notnull=True)
        tbl.column('max_beds', dtype='N', name_long='Max Beds', name_short='Beds')
        tbl.column('facility_type_id', size=':10', name_long='Facility Type', validate_notnull=True)\
            .relation('host.facility_type.code', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')
    
        tbl.aliasColumn('comune_id', '@anagrafica_id.comune_id', name_long='Municipality').relation(
                    'glbl.comune.id', mode='foreignkey')

        # Alias columns from anagrafica
        tbl.aliasColumn('facility_type_code', '@facility_type_id.code', name_long='Type Code')
        tbl.aliasColumn('facility_type_description', '@facility_type_id.description',
                       name_long='Type Description')
        tbl.aliasColumn('comune_denominazione', '@comune_id.denominazione', name_long='Municipality Name')
        tbl.aliasColumn('comune_sigla_provincia', '@comune_id.sigla_provincia', name_long='Province')
