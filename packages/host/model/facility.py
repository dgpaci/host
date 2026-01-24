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
            .relation('erpy_base.anagrafica.id', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')

        tbl.column('name', size=':100', name_long='Facility Name', validate_notnull=True)

        tbl.column('facility_type_id', size='22', name_long='Facility Type', validate_notnull=True)\
            .relation('host.facility_type.id', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')

        tbl.column('comune_id', size='22', name_long='Municipality', validate_notnull=True)\
            .relation('glbl.comune.id', mode='foreignkey',
                     relation_name='facilities', onDelete='raise')

        # Alias columns from anagrafica
        tbl.aliasColumn('owner_name', '@anagrafica_id.ragione_sociale', name_long='Owner Name')
        tbl.aliasColumn('facility_type_code', '@facility_type_id.code', name_long='Type Code')
        tbl.aliasColumn('facility_type_description', '@facility_type_id.description',
                       name_long='Type Description')
        tbl.aliasColumn('comune_nome', '@comune_id.nome', name_long='Municipality Name')
        tbl.aliasColumn('comune_sigla_provincia', '@comune_id.sigla_provincia', name_long='Province')
