#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Stay table - accommodation period"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'stay',
            pkey='id',
            name_long='Stay',
            name_plural='Stays',
            caption_field='stay_caption'
        )

        self.sysFields(tbl)

        tbl.column('facility_id', size='22', name_long='Facility', validate_notnull=True)\
            .relation('host.facility.id', mode='foreignkey',
                     relation_name='stays', onDelete='raise')

        tbl.column('check_in_date', dtype='D', name_long='Check-in Date', validate_notnull=True,
                   name_short='Check-in')

        tbl.column('check_out_date', dtype='D', name_long='Check-out Date', validate_notnull=True,
                   name_short='Check-out')

        tbl.column('arrival_time', dtype='H', name_long='Arrival Time',
                   name_short='Arrival')

        tbl.column('flight_number', size='20', name_long='Flight Number',
                   name_short='Flight')

        tbl.column('safe_code', size='4', name_long='Safe Code',
                   name_short='Safe')

        # Calculated field: number of nights
        tbl.formulaColumn('nights', "($check_out_date - $check_in_date)",
                         dtype='I', name_long='Number of Nights', name_short='Nights')

        # Alias columns
        tbl.aliasColumn('facility_name', '@facility_id.name', name_long='Facility Name')
        tbl.aliasColumn('facility_type', '@facility_id.@facility_type_id.description',
                       name_long='Facility Type')

        # Virtual column for caption (will be set via formula)
        tbl.formulaColumn('stay_caption',
                         """$facility_name || ' - ' || COALESCE(TO_CHAR($check_in_date, 'DD/MM/YYYY'), 'N/A')""",
                         name_long='Stay Caption')
        
        tbl.formulaColumn('group_leader_name', select=dict(
                        table='host.guest',
                        where='$stay_id=#THIS.id AND $is_group_leader IS TRUE',
                        columns='$full_name'), name_long='Group Leader Name')

    def trigger_onInserting(self, record=None, **kwargs):
        """Validate dates before insert"""
        self._validate_dates(record)

    def trigger_onUpdating(self, record=None, old_record=None, **kwargs):
        """Validate dates before update"""
        self._validate_dates(record)

    def _validate_dates(self, record):
        """Ensure check-out date is after check-in date"""
        check_in = record.get('check_in_date')
        check_out = record.get('check_out_date')

        if check_in and check_out and check_out <= check_in:
            raise Exception("Check-out date must be after check-in date")
