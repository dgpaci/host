#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrbag import Bag
from gnr.core.gnrbag import Bag
from datetime import date

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

        tbl.column('document_issued_by_provincia', size='2', name_long='!![en]Document Issued By (Province)',
                   name_short='!![en]Issued By (Prov.)')\
            .relation('glbl.provincia.sigla', mode='foreignkey',
                     relation_name='issued_documents', onDelete='setnull')

        tbl.column('document_issued_by_country', size='2', name_long='!![en]Document Issued By (Country)',
                   name_short='!![en]Issued By (Country)')\
            .relation('glbl.nazione.code', mode='foreignkey',
                     relation_name='issued_documents', onDelete='setnull')

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
        tbl.aliasColumn('age', '@anagrafica_id.eta', name_long='!![en]Age')

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
        if not record.get('tourist_tax_code'):
            record['tourist_tax_code'] = self._guess_tourist_tax_code(record)
        self.calculateTaxAmount(record)

    def trigger_onUpdating(self, record=None, old_record=None, **kwargs):
        if self.fieldsChanged('tourist_tax_code', record, old_record):
            pass  # user forced the tax code; keep it
        else:
            guessed_code = self._guess_tourist_tax_code(record)
            guessed_old = self._guess_tourist_tax_code(old_record)
            current_code = record.get('tourist_tax_code')
            if current_code and current_code != guessed_old:
                pass  # keep the previously forced value
            else:
                record['tourist_tax_code'] = guessed_code
        self.calculateTaxAmount(record)
        self.notifyDbUpdate(record['id'])

    def _guess_tourist_tax_code(self, record):
        stay_id = record.get('stay_id')
        anagrafica_id = record.get('anagrafica_id')

        if not (stay_id and anagrafica_id):
            return self.db.application.getPreference('tourist_tax_default_code', pkg='host') or '0000000005'

        stay = self.db.table('host.stay').record(pkey=stay_id).output('dict')
        facility_id = stay.get('facility_id') if stay else None
        check_in_date = stay.get('check_in_date') if stay else None

        if not facility_id:
            return self.db.application.getPreference('tourist_tax_default_code', pkg='host') or '0000000005'

        comune_id, localita = self.db.table('host.facility').readColumns(
            pkey=facility_id,
            columns='@anagrafica_id.comune_id,@anagrafica_id.localita'
        )

        if not (comune_id or localita):
            return self.db.application.getPreference('tourist_tax_default_code', pkg='host') or '0000000005'

        if comune_id:
            municipality_pattern = f"%_{comune_id}"
        else:
            municipality_pattern = f"%_{localita.upper()}"

        tax_municipalities = self.db.table('host.tourist_tax_municipality').query(
            where='$municipality_key LIKE :pattern',
            pattern=municipality_pattern
        ).fetch()

        fallback_code = None
        for tax_mun in tax_municipalities:
            exemption_conditions = tax_mun.get('exemption_conditions')
            if not exemption_conditions:
                if not fallback_code:
                    fallback_code = tax_mun.get('tourist_tax_code')
                continue
            is_exempt = self._evaluate_exemption_conditions(
                exemption_conditions=exemption_conditions,
                record=record
            )
            if is_exempt:
                return tax_mun.get('tourist_tax_code')

        return fallback_code or self.db.application.getPreference('tourist_tax_default_code', pkg='host') or '0000000005'

    def _evaluate_exemption_conditions(self, exemption_conditions=None, record=None, guest_id=None, **kwargs):
        """
        Evaluate exemption conditions from bag against guest data.
        Returns True if all conditions are met (guest is exempt).

        Follows the pattern from compileCustomizedQuestions in webex.registration_form

        Conditions format in bag:
        - column: column name from guest table (e.g., 'age', 'citizenship')
        - operator: comparison operator ('<', '>', '==', '!=', '<=', '>=')
        - value: comparison value (fixed value or column reference with $)
        """
        if not exemption_conditions:
            return False

        conditions = exemption_conditions.values() if isinstance(exemption_conditions, Bag) else exemption_conditions
        record = record or {}
        guest_id = guest_id or record.get('id')

        for condition in conditions:
            parsed = self._parse_exemption_condition(condition)
            if not parsed:
                continue

            left_expr = parsed['left']
            operator = parsed['operator']
            right_expr = parsed['right']

            left_value = self._resolve_condition_value(left_expr, record=record, guest_id=guest_id)
            right_value = self._resolve_condition_value(right_expr, record=record, guest_id=guest_id, literal_ok=True)

            if left_value is None:
                return False

            try:
                left_value, right_value = self._coerce_for_compare(left_value, right_value, operator)
                if operator == '<':
                    if not (left_value < right_value):
                        return False
                elif operator == '>':
                    if not (left_value > right_value):
                        return False
                elif operator == '<=':
                    if not (left_value <= right_value):
                        return False
                elif operator == '>=':
                    if not (left_value >= right_value):
                        return False
                elif operator == '==':
                    if not (left_value == right_value):
                        return False
                elif operator == '!=':
                    if not (left_value != right_value):
                        return False
                else:
                    return False
            except (TypeError, ValueError):
                return False

        return True

    def _parse_exemption_condition(self, condition):
        if isinstance(condition, dict):
            column = condition.get('column')
            operator = condition.get('operator')
            value = condition.get('value')
            if not column or not operator:
                return None
            left = column if column.startswith(('$', '@')) else f'${column}'
            return dict(left=left, operator=operator, right=value)

        if hasattr(condition, 'get'):
            column = condition.get('column')
            operator = condition.get('operator')
            value = condition.get('value')
            if not column or not operator:
                return None
            left = column if column.startswith(('$', '@')) else f'${column}'
            return dict(left=left, operator=operator, right=value)

        if isinstance(condition, str):
            raw = condition.strip()
            for op in ('<=', '>=', '==', '!=', '<', '>'):
                if op in raw:
                    left, right = [p.strip() for p in raw.split(op, 1)]
                    left = left if left.startswith(('$', '@')) else f'${left}'
                    return dict(left=left, operator=op, right=right)
        return None

    def _resolve_condition_value(self, expr, record=None, guest_id=None, literal_ok=False):
        if expr is None:
            return None
        if not isinstance(expr, str):
            return expr

        raw = expr.strip()
        if not raw:
            return None

        if not raw.startswith(('$', '@')):
            return self._coerce_literal(raw) if literal_ok else raw

        if guest_id:
            if raw.startswith('$'):
                return self.readColumns(where='$id=:guest_id', guest_id=guest_id, columns=f'${raw[1:]}')
            return self.readColumns(where='$id=:guest_id', guest_id=guest_id, columns=raw)

        record = record or {}

        if raw.startswith('$'):
            column = raw[1:]
            if column in record:
                return record.get(column)
            return None

        if raw.startswith('@stay_id.'):
            stay_id = record.get('stay_id')
            if stay_id:
                tail = raw[len('@stay_id.'):]
                if tail and tail[0] not in '@$':
                    tail = f'${tail}'
                return self.db.table('host.stay').readColumns(pkey=stay_id, columns=tail)
            return None

        if raw.startswith('@anagrafica_id.'):
            anagrafica_id = record.get('anagrafica_id')
            if anagrafica_id:
                tail = raw[len('@anagrafica_id.'):]
                if tail and tail[0] not in '@$':
                    tail = f'${tail}'
                return self.db.table('er_core.anagrafica').readColumns(pkey=anagrafica_id, columns=tail)
            return None

        return None

    def _coerce_literal(self, value):
        if not isinstance(value, str):
            return value
        v = value.strip()
        if not v:
            return v
        low = v.lower()
        if low in ('true', 'false'):
            return low == 'true'
        try:
            if v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
                return int(v)
            return float(v)
        except ValueError:
            pass
        try:
            return date.fromisoformat(v)
        except ValueError:
            return v

    def _coerce_for_compare(self, left_value, right_value, operator):
        if operator in ('<', '>', '<=', '>='):
            if isinstance(left_value, str):
                left_value = self._coerce_literal(left_value)
            if isinstance(right_value, str):
                right_value = self._coerce_literal(right_value)
        return left_value, right_value

    def calculateTaxAmount(self, record, stay_id=None, tourist_tax_code=None, **kwargs):
        stay_id = stay_id or record.get('stay_id')
        tourist_tax_code = tourist_tax_code or record.get('tourist_tax_code')

        if not (stay_id and tourist_tax_code):
            record['tax_amount'] = 0
            return

        stay_rec = self.db.table('host.stay').record(pkey=stay_id, virtual_columns='$nights').output('bag')
        if not stay_rec or not stay_rec.get('nights'):
            record['tax_amount'] = 0
            return

        nights = stay_rec.get('nights', 0)
        comune_id, localita = self.db.table('host.facility').readColumns(
                                pkey=stay_rec['facility_id'],
                                columns='@anagrafica_id.comune_id,@anagrafica_id.localita')

        if comune_id:
            municipality_key = f"{tourist_tax_code}_{comune_id}"
        elif localita:
            municipality_key = f"{tourist_tax_code}_{localita.upper()}"
        else:
            record['tax_amount'] = 0
            return

        tax_municipality = self.db.table('host.tourist_tax_municipality').record(
            where='$municipality_key=:key',
            key=municipality_key
        ).output('bag')

        tax_rate = tax_municipality.get('amount', 0)

        if not tax_rate:
            record['tax_amount'] = 0
            return

        exemption_conditions = tax_municipality.get('exemption_conditions')
        if exemption_conditions:
            is_exempt = self._evaluate_exemption_conditions(
                                exemption_conditions=exemption_conditions,
                                record=record, **kwargs)
            if is_exempt:
                record['tax_amount'] = 0
                return

        max_nights = tax_municipality.get('max_nights')
        if max_nights and max_nights > 0:
            taxable_nights = min(nights, max_nights)
        else:
            taxable_nights = nights

        record['tax_amount'] = taxable_nights * tax_rate
