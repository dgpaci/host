#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrbag import Bag
from gnr.core.gnrbag import Bag
from datetime import date
from gnr.app import pkglog as logger

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
        tbl.aliasColumn('age', '@anagrafica_id.eta', dtype='I', name_long='!![en]Age', static=True)

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

    def trigger_onInserted(self, record=None, **kwargs):
        with self.recordToUpdate(record['id']) as record:
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
            return None

        facility_id = self.db.table('host.stay').readColumns(pkey=stay_id, columns='$facility_id')
        if not facility_id:
            return None

        comune_id, localita = self.db.table('host.facility').readColumns(
            pkey=facility_id,
            columns='@anagrafica_id.comune_id,@anagrafica_id.localita'
        )

        if not (comune_id or localita):
            return None

        tax_rows = self._tax_rows_for_location(comune_id=comune_id, localita=localita)

        match_row = self._match_tax_row(record, tax_rows)
        if match_row:
            matched_code = match_row.get('tourist_tax_code')
            return matched_code

        default_code = self.db.application.getPreference('tourist_tax_default_code', pkg='host')
        if default_code:
            logger.info("Using default tax code from preferences: %s for guest_id=%s",
                       default_code, record.get('id'))
            return default_code

        return None

    def _evaluate_exemption_conditions(self, exemption_conditions=None, record=None, **kwargs):
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

        any_condition = False
        for condition in conditions:
            parsed = self._parse_exemption_condition(condition)
            if not parsed:
                continue
            any_condition = True

            left_expr = parsed['left']
            operator = parsed['operator']
            right_expr = parsed['right']

            left_value = self._resolve_condition_value(left_expr, record=record)
            right_value = self._resolve_condition_value(right_expr, record=record, literal_ok=True)

            logger.info("Evaluating: %s %s %s -> left=%s right=%s (guest_id=%s)",
                       left_expr, operator, right_expr, left_value, right_value, record.get('id'))

            if left_value is None:
                logger.info("left_value is None for guest_id=%s, returning False", record.get('id'))
                return False

            try:
                left_value, right_value = self._coerce_for_compare(left_value, right_value, operator)
                if operator == '<':
                    if not (left_value < right_value):
                        logger.info("Condition not met: %s < %s", left_value, right_value)
                        return False
                elif operator == '>':
                    if not (left_value > right_value):
                        logger.info("Condition not met: %s > %s", left_value, right_value)
                        return False
                elif operator == '<=':
                    if not (left_value <= right_value):
                        logger.info("Condition not met: %s <= %s", left_value, right_value)
                        return False
                elif operator == '>=':
                    if not (left_value >= right_value):
                        logger.info("Condition not met: %s >= %s", left_value, right_value)
                        return False
                elif operator == '==':
                    if not (left_value == right_value):
                        logger.info("Condition not met: %s == %s", left_value, right_value)
                        return False
                elif operator == '!=':
                    if not (left_value != right_value):
                        logger.info("Condition not met: %s != %s", left_value, right_value)
                        return False
                else:
                    return False
            except (TypeError, ValueError) as e:
                logger.info("Exception in condition evaluation: %s (guest_id=%s)", e, record.get('id'))
                return False

        return True if any_condition else False

    def _parse_exemption_condition(self, condition):

        # Normalize Bag containers
        if isinstance(condition, Bag):
            # If bag has direct keys column/operator/value
            try:
                as_dict = condition.asDict(ascii=True)
                if isinstance(as_dict, dict) and {'column', 'operator', 'value'}.intersection(as_dict.keys()):
                    condition = as_dict
            except Exception:
                pass
            # If bag is a wrapper with a single child
            if not isinstance(condition, dict) and len(condition) == 1:
                try:
                    child = list(condition.values())[0]
                    if isinstance(child, Bag):
                        condition = child.asDict(ascii=True)
                    else:
                        condition = child
                except Exception:
                    pass

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

    def _resolve_condition_value(self, expr, record=None, literal_ok=False):
        if expr is None:
            return None
        if not isinstance(expr, str):
            return expr

        raw = expr.strip()
        if not raw:
            return None

        if not raw.startswith(('$', '@')):
            return self._coerce_literal(raw) if literal_ok else raw
        else:
            column = raw[1:]
            if column in record:
                return record.get(column)
            value = self.readColumns(record['id'], columns=raw)
            if value:
                return value
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

    def _tax_rows_for_location(self, comune_id=None, localita=None):
        if comune_id:
            municipality_pattern = f"%_{comune_id}"
        elif localita:
            municipality_pattern = f"%_{localita.upper()}"
        else:
            return []
        rows = self.db.table('host.tourist_tax_municipality').query(
            where='$municipality_key LIKE :pattern',
            pattern=municipality_pattern,
            columns='$tourist_tax_code,$amount,$exemption_conditions,$municipality_key',
            bagFields=True
        ).fetch()
        return rows

    def _match_tax_row(self, record, tax_rows):
        matches = []

        for row in tax_rows:
            exemption_conditions = row.get('exemption_conditions')

            if isinstance(exemption_conditions, str):
                exemption_conditions = Bag(exemption_conditions)

            if not exemption_conditions or (isinstance(exemption_conditions, Bag) and len(exemption_conditions) == 0):
                continue

            is_match = self._evaluate_exemption_conditions(
                exemption_conditions=exemption_conditions,
                record=record
            )
            logger.info("_evaluate_exemption_conditions returned: %s for guest_id=%s", is_match, record.get('id'))

            if is_match:
                logger.info("MATCH found! tax_code=%s amount=%s for guest_id=%s",
                           row.get('tourist_tax_code'), row.get('amount'), record.get('id'))
                matches.append(row)

        if matches:
            best_match = min(matches, key=lambda r: r.get('amount') if r.get('amount') is not None else 0)
            logger.info("Best match selected: tax_code=%s amount=%s for guest_id=%s",
                       best_match.get('tourist_tax_code'), best_match.get('amount'), record.get('id'))
            return best_match

        logger.info("No exemption condition matches for guest_id=%s", record.get('id'))
        return None

    def calculateTaxAmount(self, record, **kwargs):
        stay_id = record.get('stay_id')
        tourist_tax_code = record.get('tourist_tax_code')

        if not (stay_id and tourist_tax_code):
            record['tax_amount'] = 0
            return

        nights, facility_id = self.db.table('host.stay').readColumns(pkey=stay_id,
                                                                     columns='$nights,$facility_id')
        if not nights:
            record['tax_amount'] = 0
            return

        comune_id, localita = self.db.table('host.facility').readColumns(
                                pkey=facility_id,
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
        if not tax_municipality:
            record['tax_amount'] = 0
            return

        tax_rate = tax_municipality.get('amount', 0)

        if not tax_rate:
            record['tax_amount'] = 0
            return

        max_nights = tax_municipality.get('max_nights')
        if max_nights and max_nights > 0:
            taxable_nights = min(nights, max_nights)
        else:
            taxable_nights = nights

        record['tax_amount'] = taxable_nights * tax_rate

    def importNewGuests(self, stay_id=None, lines=None, first=None):
        guest_payloads = self._build_guest_payloads(lines=lines, first=first)
        anagrafica_table = self.db.table('er_core.anagrafica')

        for p in guest_payloads:
            anagrafica_record = anagrafica_table.newrecord(
                cognome=p['surname'],
                nome=p['name'],
                ragione_sociale=f"{p['surname']} {p['name']}".strip(),
                sesso=p['gender'],
                data_nascita=p['birth_dt'],
                comune_nascita=p['birth_comune'],
                luogo_nascita=p['birth_comune'] or '',
                provincia_nascita=p['birth_prov'],
                nazione_nascita=p['birth_country_code'],
                stato_nascita=p['birth_country_code'],
                cittadinanza=p['citizenship_code']
            )

            anagrafica_table.insert(anagrafica_record)

            guest_record = self.newrecord(
                stay_id=stay_id,
                anagrafica_id=anagrafica_record.get('id'),
                guest_type_code=p['guest_type'],
                assignId=True
            )

            if p['doc_type'] or p['doc_number']:
                guest_record['document_type_code'] = p['doc_type'] or None
                guest_record['document_number'] = p['doc_number'] or None
                if p['doc_prov']:
                    guest_record['document_issued_by_provincia'] = p['doc_prov']

            self.insert(guest_record)
                                
    def _build_guest_payloads(self, lines, first):
        payloads = []
        for idx, raw in enumerate(lines, 1):
            if len(raw) < 168:
                continue

            guest_type = raw[0:2].strip()
            arrival_date = raw[2:12].strip()
            days_of_stay = raw[12:14].strip()
            surname = raw[14:64].strip()
            name = raw[64:94].strip()
            gender_code = raw[94:95].strip()
            birth_date = raw[95:105].strip()
            birth_mun_istat = raw[105:114].strip()
            birth_prov = raw[114:116].strip()
            birth_country = raw[116:125].strip()
            citizenship = raw[125:134].strip()
            doc_type = raw[134:139].strip()
            doc_number = raw[139:159].strip()
            doc_issue_place = raw[159:168].strip()

            if arrival_date != first[2:12].strip() or days_of_stay != first[12:14].strip():
                logger.warning("Importer line %s arrival/days differ", idx)

            gender = 'M' if gender_code == '1' else 'F' if gender_code == '2' else None
            birth_dt = self._parse_ddmmyyyy(birth_date)

            birth_comune, birth_prov_from_istat = self._resolve_comune_from_istat(birth_mun_istat)
            _, doc_prov = self._resolve_comune_from_istat(doc_issue_place)

            birth_country_code = self._resolve_country_from_istat(birth_country)
            citizenship_code = self._resolve_country_from_istat(citizenship)

            payloads.append(dict(
                idx=idx,
                guest_type=guest_type,
                surname=surname,
                name=name,
                gender=gender,
                birth_dt=birth_dt,
                birth_comune=birth_comune,
                birth_prov=birth_prov or birth_prov_from_istat,
                birth_country_code=birth_country_code,
                citizenship_code=citizenship_code,
                doc_type=doc_type,
                doc_number=doc_number,
                doc_prov=doc_prov,
                birth_date=birth_date
            ))
        return payloads