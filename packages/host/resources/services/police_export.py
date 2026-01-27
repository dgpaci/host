#!/usr/bin/env python
# encoding: utf-8

"""
Police Report Export Service
Generates TXT file with 178 characters per guest following Italian police requirements
"""

from datetime import datetime

class PoliceExportService(object):
    """Service to export guest data in police-required format"""

    def __init__(self, db):
        self.db = db

    def export_stay(self, stay_id):
        """
        Export all guests for a specific stay
        Returns string with 178 characters per guest
        """
        stay = self.db.table('host.stay').record(pkey=stay_id).output('dict')
        if not stay:
            raise Exception(f"Stay {stay_id} not found")

        guests = self.db.table('host.guest').query(
            where='$stay_id=:stay_id',
            stay_id=stay_id,
            order_by='@guest_type_code.code, @anagrafica_id.cognome'
        ).fetch()

        lines = []
        for guest in guests:
            line = self._format_guest_line(stay, guest)
            lines.append(line)

        return '\n'.join(lines)

    def _format_guest_line(self, stay, guest):
        """
        Format a single guest line (178 characters)
        """
        anagrafica = self.db.table('er_core.anagrafica').record(
            pkey=guest['anagrafica_id']
        ).output('dict')

        # Get guest type code
        guest_type_rec = self.db.table('host.guest_type').record(
            pkey=guest['guest_type_code']
        ).output('dict')
        guest_type = guest_type_rec.get('code', '20') if guest_type_rec else '20'

        # Build the 178-character line
        parts = []

        # 1. Tipo Alloggiato (2 chars)
        parts.append(self._pad(guest_type, 2, 'N'))

        # 2. Data di Arrivo (10 chars) - format: gg/mm/aaaa
        check_in = stay.get('check_in_date')
        if check_in:
            check_in_str = check_in.strftime('%d/%m/%Y') if hasattr(check_in, 'strftime') else str(check_in)
        else:
            check_in_str = ''
        parts.append(self._pad(check_in_str, 10, 'AN'))

        # 3. Numero Giorni di Permanenza (2 chars)
        nights = str(stay.get('nights', 0))
        parts.append(self._pad(nights, 2, 'N'))

        # 4. Cognome (50 chars)
        surname = anagrafica.get('cognome', '')
        parts.append(self._pad(surname, 50, 'A'))

        # 5. Nome (30 chars)
        name = anagrafica.get('nome', '')
        parts.append(self._pad(name, 30, 'A'))

        # 6. Sesso (1 char) - 1=M, 2=F
        gender = anagrafica.get('sesso', '')
        gender_code = '1' if gender == 'M' else '2' if gender == 'F' else ' '
        parts.append(self._pad(gender_code, 1, 'N'))

        # 7. Data di Nascita (10 chars) - format: gg/mm/aaaa
        birth_date = anagrafica.get('data_nascita')
        if birth_date:
            birth_str = birth_date.strftime('%d/%m/%Y') if hasattr(birth_date, 'strftime') else str(birth_date)
        else:
            birth_str = ''
        parts.append(self._pad(birth_str, 10, 'AN'))

        # 8. Comune di Nascita (9 chars) - ISTAT code
        birth_comune = self._get_comune_istat(anagrafica.get('comune_nascita', ''))
        parts.append(self._pad(birth_comune, 9, 'N'))

        # 9. Provincia di Nascita (2 chars)
        birth_province = anagrafica.get('provincia_nascita', '')
        parts.append(self._pad(birth_province, 2, 'A'))

        # 10. Stato di Nascita (9 chars) - country code
        birth_country = self._get_country_code(anagrafica.get('stato_nascita', ''))
        parts.append(self._pad(birth_country, 9, 'N'))

        # 11. Cittadinanza (9 chars) - citizenship code
        citizenship = self._get_country_code(anagrafica.get('cittadinanza', ''))
        parts.append(self._pad(citizenship, 9, 'N'))

        # 12. Tipo di Documento (5 chars)
        doc_type = ''
        if guest.get('document_type_code'):
            doc_type_rec = self.db.table('host.document_type').record(
                pkey=guest['document_type_code']
            ).output('dict')
            doc_type = doc_type_rec.get('code', '') if doc_type_rec else ''
        parts.append(self._pad(doc_type, 5, 'AN'))

        # 13. Numero del Documento (20 chars)
        doc_number = guest.get('document_number', '')
        parts.append(self._pad(doc_number, 20, 'AN'))

        # 14. Luogo di Rilascio del Documento (9 chars) - comune code
        doc_place = self._get_comune_istat(guest.get('document_issued_by', ''))
        parts.append(self._pad(doc_place, 9, 'N'))

        # 15. Codice tariffa imposta soggiorno (10 chars) - optional
        tax_code = ''
        if guest.get('tourist_tax_code'):
            tax_rec = self.db.table('host.tourist_tax').record(
                pkey=guest['tourist_tax_code']
            ).output('dict')
            tax_code = tax_rec.get('code', '') if tax_rec else ''
        parts.append(self._pad(tax_code, 10, 'N'))

        # Join all parts (should be exactly 178 characters)
        line = ''.join(parts)

        if len(line) != 178:
            raise Exception(f"Invalid line length: {len(line)} (expected 178)")

        return line

    def _pad(self, value, length, field_type):
        """
        Pad value to specified length
        field_type: 'A' = alpha, 'N' = numeric, 'AN' = alphanumeric
        """
        if value is None:
            value = ''

        value = str(value).strip()

        # For numeric fields, pad left with zeros
        if field_type == 'N':
            value = value.replace('/', '').replace('-', '').replace(' ', '')
            return value.zfill(length)[:length]

        # For alpha/alphanumeric, pad right with spaces
        return value.ljust(length)[:length]

    def _get_comune_istat(self, comune_name):
        """Get ISTAT code for comune (municipality)"""
        if not comune_name:
            return ''

        # Query glbl.comune table for ISTAT code
        comune = self.db.table('glbl.comune').query(
            where='$nome=:nome',
            nome=comune_name
        ).fetchone()

        if comune:
            return comune.get('code_istat', '')

        return ''

    def _get_country_code(self, country_code):
        """Get numeric country code from glbl.nazione"""
        if not country_code:
            return ''

        # If already numeric, return as-is
        if country_code.isdigit():
            return country_code

        # Query glbl.nazione for numeric code
        country = self.db.table('glbl.nazione').query(
            where='$code=:code',
            code=country_code
        ).fetchone()

        if country:
            # Assuming there's a numeric code field
            return country.get('code_istat', '') or country.get('code', '')

        return ''


def export_stay_to_file(db, stay_id, output_path=None):
    """
    Convenience function to export stay to file
    """
    service = PoliceExportService(db)
    content = service.export_stay(stay_id)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return output_path
    else:
        # Return content for download
        return content
