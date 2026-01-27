#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Guest table - each guest belongs to one stay"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'guest',
            pkey='id',
            name_long='!![en]Guest',
            name_plural='!![en]Guests',
            caption_field='full_name'
        )

        self.sysFields(tbl)

        tbl.column('stay_id', size='22', name_long='!![en]Stay', validate_notnull=True)\
            .relation('host.stay.id', mode='foreignkey',
                     relation_name='guests', onDelete='cascade')

        tbl.column('anagrafica_id', size='22', name_long='!![en]Guest Registry', validate_notnull=True)\
            .relation('er_core.anagrafica.id', mode='foreignkey',
                     relation_name='guest_records', onDelete='raise')

        tbl.column('guest_type_code', size=':2', name_long='!![en]Guest Type', validate_notnull=True)\
            .relation('host.guest_type.code', mode='foreignkey',
                     relation_name='guests', onDelete='raise')

        tbl.column('tourist_tax_code', size=':15', name_long='!![en]Tourist Tax Rate')\
            .relation('host.tourist_tax.code', mode='foreignkey',
                     relation_name='guests', onDelete='setnull')

        # Document fields (required only for group leaders)
        tbl.column('document_type_code', size=':10', name_long='!![en]Document Type')\
            .relation('host.document_type.code', mode='foreignkey',
                     relation_name='guests', onDelete='setnull')

        tbl.column('document_number', size=':20', name_long='!![en]Document Number')

        tbl.column('document_issued_by', size=':100', name_long='!![en]Document Issued By',
                   name_short='!![en]Issued By')

        tbl.column('document_issue_date', dtype='D', name_long='!![en]Document Issue Date',
                   name_short='!![en]Issue Date')

        tbl.column('document_expiry_date', dtype='D', name_long='!![en]Document Expiry Date',
                   name_short='!![en]Expiry Date')

        tbl.column('tax_amount', dtype='N', size='12,2', name_long='!![en]Total Tax Amount',
                   name_short='!![en]Tax Amount', default=0)

        # Alias columns from anagrafica
        tbl.aliasColumn('surname', '@anagrafica_id.cognome', name_long='!![en]Surname')
        tbl.aliasColumn('name', '@anagrafica_id.nome', name_long='!![en]Name')
        tbl.aliasColumn('full_name', '@anagrafica_id.ragione_sociale', name_long='!![en]Full Name')
        tbl.aliasColumn('gender', '@anagrafica_id.sesso', name_long='!![en]Gender')
        tbl.aliasColumn('birth_date', '@anagrafica_id.data_nascita', name_long='!![en]Birth Date', name_short='!![en]Birth D.')
        tbl.aliasColumn('birth_place', '@anagrafica_id.luogo_nascita', name_long='!![en]Birth Place')
        tbl.aliasColumn('birth_province', '@anagrafica_id.provincia_nascita', name_long='!![en]Birth Province')
        tbl.aliasColumn('birth_country', '@anagrafica_id.nazione_nascita', name_long='!![en]Birth Country')
        tbl.aliasColumn('citizenship', '@anagrafica_id.cittadinanza', name_long='!![en]Citizenship')

        guest = tbl.colgroup('guest', name_long='!![en]Guest Information')
        guest.aliasColumn('guest_type_description', '@guest_type_code.description',
                       name_long='!![en]Guest Type')
        guest.aliasColumn('is_group_leader', '@guest_type_code.is_leader', static=True,
                       name_long='!![en]Is Group Leader')
        guest.aliasColumn('document_type_description', '@document_type_code.description',
                       name_long='!![en]Doc Type Description')
        tbl.aliasColumn('tax_description', '@tourist_tax_code.description', name_long='!![en]Tax Description')

        # Alias columns from stay
        tbl.aliasColumn('stay_nights', '@stay_id.nights', name_long='!![en]Nights')
        tbl.aliasColumn('stay_check_in', '@stay_id.check_in_date', name_long='!![en]Check-in')
        tbl.aliasColumn('stay_check_out', '@stay_id.check_out_date', name_long='!![en]Check-out')
        tbl.aliasColumn('facility_name', '@stay_id.@facility_id.name', name_long='!![en]Facility')
        tbl.aliasColumn('facility_id', '@stay_id.facility_id', name_long='!![en]Facility ID')
        tbl.aliasColumn('facility_comune_id', '@stay_id.@facility_id.comune_id', name_long='!![en]Facility Municipality ID')

    def trigger_onInserting(self, record=None, **kwargs):
        """Calculate tax amount on insert"""
        self._calculate_tax_amount(record)

    def trigger_onUpdating(self, record=None, old_record=None, **kwargs):
        """Recalculate tax amount on update"""
        self._calculate_tax_amount(record)

    def _calculate_tax_amount(self, record):
        """
        Calculate total tax amount based on:
        - Number of nights from stay
        - Tax rate from tourist_tax (per municipality)
        """
        stay_id = record.get('stay_id')
        tourist_tax_code = record.get('tourist_tax_code')

        if not (stay_id and tourist_tax_code):
            record['tax_amount'] = 0
            return

        # Get stay and facility information
        stay = self.db.table('host.stay').record(pkey=stay_id).output('dict')
        if not stay or not stay.get('nights'):
            record['tax_amount'] = 0
            return

        nights = stay.get('nights', 0)
        facility_id = stay.get('facility_id')

        if not facility_id:
            record['tax_amount'] = 0
            return

        # Get facility comune
        facility = self.db.table('host.facility').record(pkey=facility_id).output('dict')
        if not facility:
            record['tax_amount'] = 0
            return

        comune_id = facility.get('comune_id')
        if not comune_id:
            record['tax_amount'] = 0
            return

        # Get tax record with amounts bag
        tax = self.db.table('host.tourist_tax').record(pkey=tourist_tax_code).output('bag')
        if not tax:
            record['tax_amount'] = 0
            return

        # Get amounts bag
        amounts_bag = tax.getItem('amounts')
        if not amounts_bag:
            record['tax_amount'] = 0
            return

        # Find the rate for this comune
        tax_rate = None
        for node_key in amounts_bag.keys():
            node = amounts_bag.getItem(node_key)
            if node and node.getItem('comune_id') == comune_id:
                tax_rate = node.getItem('amount', 0)
                break

        if tax_rate is None or tax_rate == 0:
            record['tax_amount'] = 0
            return

        # Calculate total
        record['tax_amount'] = nights * tax_rate
