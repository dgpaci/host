#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Guest table - links to erpy_base.anagrafica for personal data"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'guest',
            pkey='id',
            name_long='Guest',
            name_plural='Guests',
            caption_field='full_name'
        )

        self.sysFields(tbl)

        tbl.column('anagrafica_id', size='22', name_long='Guest Registry', validate_notnull=True)\
            .relation('erpy_base.anagrafica.id', mode='foreignkey',
                     relation_name='guest_records', onDelete='raise')

        # Document fields (required only for group leaders)
        tbl.column('document_type_id', size='22', name_long='Document Type')\
            .relation('host.document_type.id', mode='foreignkey',
                     relation_name='guests', onDelete='setnull')

        tbl.column('document_number', size=':20', name_long='Document Number')

        tbl.column('document_issued_by', size=':100', name_long='Document Issued By',
                   name_short='Issued By')

        tbl.column('document_issue_date', dtype='D', name_long='Document Issue Date',
                   name_short='Issue Date')

        tbl.column('document_expiry_date', dtype='D', name_long='Document Expiry Date',
                   name_short='Expiry Date')

        # Alias columns from anagrafica (for convenience)
        tbl.aliasColumn('surname', '@anagrafica_id.cognome', name_long='Surname')
        tbl.aliasColumn('name', '@anagrafica_id.nome', name_long='Name')
        tbl.aliasColumn('full_name', '@anagrafica_id.ragione_sociale', name_long='Full Name')
        tbl.aliasColumn('gender', '@anagrafica_id.sesso', name_long='Gender')
        tbl.aliasColumn('birth_date', '@anagrafica_id.data_nascita', name_long='Birth Date')
        tbl.aliasColumn('birth_place', '@anagrafica_id.luogo_nascita', name_long='Birth Place')
        tbl.aliasColumn('birth_province', '@anagrafica_id.provincia_nascita', name_long='Birth Province')
        tbl.aliasColumn('birth_country', '@anagrafica_id.stato_nascita', name_long='Birth Country')
        tbl.aliasColumn('citizenship', '@anagrafica_id.cittadinanza', name_long='Citizenship')
        tbl.aliasColumn('document_type_code', '@document_type_id.code', name_long='Doc Type Code')
        tbl.aliasColumn('document_type_description', '@document_type_id.description',
                       name_long='Doc Type Description')
