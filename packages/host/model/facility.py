#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Accommodation Facility table"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'facility',
            pkey='id',
            name_long='!![en]Facility',
            name_plural='!![en]Facilities',
            caption_field='name'
        )

        self.sysFields(tbl)

        tbl.column('anagrafica_id', size='22', name_long='!![en]Owner/Manager', validate_notnull=True)\
            .relation('er_core.anagrafica.id', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')

        tbl.column('name', size=':100', name_long='!![en]Facility Name', validate_notnull=True)
        tbl.column('max_beds', dtype='N', name_long='!![en]Max Beds', name_short='!![en]Beds')
        tbl.column('facility_type_code', size=':10', name_long='!![en]Facility Type', validate_notnull=True)\
            .relation('host.facility_type.code', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')

        tbl.aliasColumn('comune_id', '@anagrafica_id.comune_id', name_long='!![en]Municipality').relation(
                    'glbl.comune.id', mode='foreignkey')
        
        tbl.aliasColumn('facility_type_description', '@facility_type_code.description',
                       name_long='!![en]Type Description')
        tbl.aliasColumn('comune_denominazione', '@comune_id.denominazione', name_long='!![en]Municipality Name')
        tbl.formulaColumn('municipality', 'COALESCE($comune_denominazione,@anagrafica_id.localita)',
                            name_long='!![en]Municipality')