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
        guest.aliasColumn('is_group_leader', '@guest_type_code.is_leader', 
                       name_long='!![en]Is Group Leader', static=True)
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

    def _evaluate_exemption_conditions(self, exemption_conditions=None, guest_id=None):
        """
        Evaluate exemption conditions from bag against guest data.
        Returns True if all conditions are met (guest is exempt).

        Follows the pattern from compileCustomizedQuestions in webex.registration_form

        Conditions format in bag:
        - column: column name from guest table (e.g., 'age', 'citizenship')
        - operator: comparison operator ('<', '>', '==', '!=', '<=', '>=')
        - value: comparison value (fixed value or column reference with $)
        """
        if not exemption_conditions or not guest_id:
            return False

        from gnr.core.gnrbag import Bag

        conditions = exemption_conditions.values() if isinstance(exemption_conditions, Bag) else exemption_conditions

        for condition in conditions:
            if not isinstance(condition, dict):
                continue

            column = condition.get('column')
            operator = condition.get('operator')
            compare_value = condition.get('value')

            if not column or not operator:
                continue

            # Read the column value from the guest table
            column_value = self.readColumns(where='$id=:guest_id', guest_id=guest_id, columns=f'${column}')

            if column_value is None:
                return False

            # If compare_value starts with $, read it from the guest table too
            if isinstance(compare_value, str) and compare_value.startswith('$'):
                compare_value = self.readColumns(where='$id=:guest_id', guest_id=guest_id, columns=f'{compare_value}')

            # Perform comparison
            try:
                if operator == '<':
                    if not (column_value < compare_value):
                        return False
                elif operator == '>':
                    if not (column_value > compare_value):
                        return False
                elif operator == '<=':
                    if not (column_value <= compare_value):
                        return False
                elif operator == '>=':
                    if not (column_value >= compare_value):
                        return False
                elif operator == '==':
                    if not (column_value == compare_value):
                        return False
                elif operator == '!=':
                    if not (column_value != compare_value):
                        return False
                else:
                    return False
            except (TypeError, ValueError):
                return False

        return True

    def _calculate_tax_amount(self, record):
        """
        Calculate total tax amount based on:
        - Number of nights from stay
        - Tax rate from tourist_tax_municipality
        - Exemption conditions evaluation
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

        # Get facility and anagrafica
        facility = self.db.table('host.facility').record(pkey=facility_id).output('dict')
        if not facility:
            record['tax_amount'] = 0
            return

        anagrafica_id = facility.get('anagrafica_id')
        if not anagrafica_id:
            record['tax_amount'] = 0
            return

        anagrafica = self.db.table('er_core.anagrafica').record(pkey=anagrafica_id).output('dict')
        if not anagrafica:
            record['tax_amount'] = 0
            return

        # Check preference for comune management
        use_comuni = self.db.application.getPreference('dati_glbl.comuni_istat', pkg='er_core')

        comune_id = None
        localita = None

        if use_comuni:
            comune_id = anagrafica.get('comune_id')
        else:
            localita = anagrafica.get('localita')

        if not comune_id and not localita:
            record['tax_amount'] = 0
            return

        # Build municipality key
        if comune_id:
            municipality_key = f"{tourist_tax_code}_{comune_id}"
        else:
            municipality_key = f"{tourist_tax_code}_{localita.upper()}"

        # Get tax rate from tourist_tax_municipality
        tax_municipality = self.db.table('host.tourist_tax_municipality').query(
            where='$municipality_key=:key',
            key=municipality_key
        ).fetchone()

        if not tax_municipality:
            record['tax_amount'] = 0
            return

        tax_rate = tax_municipality.get('amount', 0)

        if not tax_rate:
            record['tax_amount'] = 0
            return

        # Check exemption conditions from municipality
        exemption_conditions = tax_municipality.get('exemption_conditions')

        # If exemption conditions exist and guest_id is available, evaluate them
        guest_id = record.get('id')
        if exemption_conditions and guest_id:
            is_exempt = self._evaluate_exemption_conditions(exemption_conditions=exemption_conditions, guest_id=guest_id)
            if is_exempt:
                record['tax_amount'] = 0
                return

        # Apply max_nights limit if set
        max_nights = tax_municipality.get('max_nights')
        if max_nights and max_nights > 0:
            taxable_nights = min(nights, max_nights)
        else:
            taxable_nights = nights

        # Calculate total
        record['tax_amount'] = taxable_nights * tax_rate
