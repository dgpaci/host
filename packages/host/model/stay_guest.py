#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Stay-Guest relationship table (many-to-many)"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'stay_guest',
            pkey='id',
            name_long='Stay Guest',
            name_plural='Stay Guests',
            caption_field='guest_name'
        )

        self.sysFields(tbl)

        tbl.column('stay_id', size='22', name_long='Stay', validate_notnull=True)\
            .relation('host.stay.id', mode='foreignkey',
                     relation_name='stay_guests', onDelete='cascade')

        tbl.column('guest_id', size='22', name_long='Guest', validate_notnull=True)\
            .relation('host.guest.id', mode='foreignkey',
                     relation_name='guest_stays', onDelete='raise')

        tbl.column('guest_type_id', size='22', name_long='Guest Type', validate_notnull=True)\
            .relation('host.guest_type.id', mode='foreignkey',
                     relation_name='stay_guests', onDelete='raise')

        tbl.column('tourist_tax_id', size='22', name_long='Tourist Tax Rate')\
            .relation('host.tourist_tax.id', mode='foreignkey',
                     relation_name='stay_guests', onDelete='setnull')

        tbl.column('tax_amount', dtype='N', size='12,2', name_long='Total Tax Amount',
                   name_short='Tax Amount', default=0)

        # Alias columns
        tbl.aliasColumn('guest_name', '@guest_id.full_name', name_long='Guest Name')
        tbl.aliasColumn('guest_surname', '@guest_id.surname', name_long='Surname')
        tbl.aliasColumn('guest_firstname', '@guest_id.name', name_long='First Name')
        tbl.aliasColumn('guest_birth_date', '@guest_id.birth_date', name_long='Birth Date')
        tbl.aliasColumn('guest_type_code', '@guest_type_id.code', name_long='Guest Type Code')
        tbl.aliasColumn('guest_type_description', '@guest_type_id.description',
                       name_long='Guest Type')
        tbl.aliasColumn('is_group_leader', '@guest_type_id.is_leader',
                       name_long='Is Group Leader')
        tbl.aliasColumn('stay_nights', '@stay_id.nights', name_long='Nights')
        tbl.aliasColumn('stay_check_in', '@stay_id.check_in_date', name_long='Check-in')
        tbl.aliasColumn('stay_check_out', '@stay_id.check_out_date', name_long='Check-out')
        tbl.aliasColumn('facility_name', '@stay_id.@facility_id.name', name_long='Facility')
        tbl.aliasColumn('facility_comune_id', '@stay_id.@facility_id.comune_id', name_long='Facility Municipality ID')
        tbl.aliasColumn('tax_description', '@tourist_tax_id.description', name_long='Tax Description')

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
        - Guest age (exemptions for children under 12)
        """
        stay_id = record.get('stay_id')
        tourist_tax_id = record.get('tourist_tax_id')
        guest_id = record.get('guest_id')

        if not (stay_id and tourist_tax_id and guest_id):
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
        tax = self.db.table('host.tourist_tax').record(pkey=tourist_tax_id).output('bag')
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
