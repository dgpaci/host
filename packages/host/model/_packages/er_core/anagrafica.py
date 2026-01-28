# encoding: utf-8

class Table(object):
    
    def trigger_onInserted(self, record=None, **kwargs):
        """Create tourist_tax_municipality records for this facility's municipality"""
        self._ensure_municipality_tax_records(record)

    def trigger_onUpdated(self, record=None, old_record=None, **kwargs):
        if self.fieldsChanged('comune_id,localita', record, old_record):
            self._ensure_municipality_tax_records(record)

    def _ensure_municipality_tax_records(self, record):
        """Ensure tourist_tax_municipality records exist for this facility's municipality"""
        tourist_taxes = self.db.table('host.tourist_tax').query(
            columns='$code'
        ).fetch()

        tax_municipality_table = self.db.table('host.tourist_tax_municipality')

        for tax in tourist_taxes:
            tax_code = tax['code']

            # Build municipality key
            if record['comune_id']:
                municipality_key = f"{tax_code}_{record['comune_id']}"
            else:
                municipality_key = f"{tax_code}_{record['localita'].upper()}"

            # Check if record already exists
            existing = tax_municipality_table.query(
                where='$municipality_key=:key',
                key=municipality_key
            ).fetch()

            if not existing:
                # Create new record
                new_record = tax_municipality_table.newrecord(
                    tourist_tax_code=tax_code,
                    comune_id=record['comune_id'],
                    localita=record['localita'],
                    amount=0)
                tax_municipality_table.insert(new_record)