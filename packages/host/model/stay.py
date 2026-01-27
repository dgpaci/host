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
                   name_short='Check-out', validate_min='$check_in_date')

        tbl.column('arrival_time', dtype='H', name_long='Arrival Time',
                   name_short='Arrival')

        tbl.column('flight_number', size='20', name_long='Flight Number',
                   name_short='Flight')

        tbl.column('safe_code', size='4', name_long='Safe Code',
                   name_short='Safe')

        tbl.column('adults_count', dtype='I', name_long='Number of Adults',
                   name_short='Adults', validate_notnull=True, default=1)
        tbl.column('children_count', dtype='I', name_long='Number of Children',
                   name_short='Children', validate_notnull=True, default=0)

        tbl.formulaColumn('nights', "($check_out_date - $check_in_date)",
                         dtype='I', name_long='Number of Nights', name_short='Nights')

        tbl.formulaColumn('total_guests', "COALESCE($adults_count, 0) + COALESCE($children_count, 0)",
                         dtype='I', name_long='Total Guests', name_short='Guests')

        # Alias columns
        tbl.aliasColumn('max_beds', '@facility_id.max_beds', name_long='Max Beds')
        tbl.aliasColumn('facility_name', '@facility_id.name', name_long='Facility Name')
        tbl.aliasColumn('facility_type', '@facility_id.@facility_type_code.description',
                       name_long='Facility Type')

        tbl.formulaColumn('stay_caption',
                         """$facility_name || ' - ' || COALESCE(TO_CHAR($check_in_date, 'DD/MM/YYYY'), 'N/A')""",
                         name_long='Stay Caption')
        
        #tbl.joinColumn('group_leader_id', name_long='Group Leader').relation('host.guest.id',
        #                cnd='@group_leader_id.stay_id=$id AND @group_leader_id.@guest_type_id.is_leader IS TRUE'
        #                ) #DP It doesn't work like this
        tbl.formulaColumn('group_leader_id', select=dict(table='host.guest',
                                                         where='$stay_id=#THIS.id AND $guest_is_leader IS TRUE',
                                                         column='$id', limit=1), name_long='Group Leader'
                          ).relation('host.guest.id', one_one='*')
        tbl.aliasColumn('group_leader_name', '@group_leader_id.full_name',
                       name_long='Group Leader Name')