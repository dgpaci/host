#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    """Stay table - accommodation period"""

    def config_db(self, pkg):
        tbl = pkg.table(
            'stay',
            pkey='id',
            name_long='!![en]Stay',
            name_plural='!![en]Stays',
            caption_field='stay_caption'
        )

        self.sysFields(tbl)

        tbl.column('facility_id', size='22', name_long='!![en]Facility', validate_notnull=True)\
            .relation('host.facility.id', mode='foreignkey',
                     relation_name='stays', onDelete='raise')

        tbl.column('check_in_date', dtype='D', name_long='!![en]Check-in Date', validate_notnull=True,
                   name_short='!![en]Check-in')

        tbl.column('check_out_date', dtype='D', name_long='!![en]Check-out Date', validate_notnull=True,
                   name_short='!![en]Check-out')

        tbl.column('arrival_time', dtype='H', name_long='!![en]Arrival Time',
                   name_short='!![en]Arrival')

        tbl.column('flight_number', size='20', name_long='!![en]Flight Number',
                   name_short='!![en]Flight')

        tbl.column('safe_code', size='4', name_long='!![en]Safe Code',
                   name_short='!![en]Safe')

        tbl.column('adults_count', dtype='I', name_long='!![en]Number of Adults',
                   name_short='!![en]Adults', validate_notnull=True, default=1)
        tbl.column('children_count', dtype='I', name_long='!![en]Number of Children',
                   name_short='!![en]Children', validate_notnull=True, default=0)

        tbl.formulaColumn('nights', "($check_out_date - $check_in_date)",
                         dtype='I', name_long='!![en]Number of Nights', name_short='!![en]Nights')

        tbl.formulaColumn('total_guests', "COALESCE($adults_count, 0) + COALESCE($children_count, 0)",
                         dtype='I', name_long='!![en]Total Guests', name_short='!![en]Guests')

        tbl.aliasColumn('max_beds', '@facility_id.max_beds', name_long='!![en]Max Beds')
        tbl.aliasColumn('facility_name', '@facility_id.name', name_long='!![en]Facility Name')
        tbl.aliasColumn('facility_type', '@facility_id.@facility_type_code.description',
                       name_long='!![en]Facility Type')

        tbl.formulaColumn('stay_caption',
                         """$facility_name || ' - ' || COALESCE(TO_CHAR($check_in_date, 'DD/MM/YYYY'), 'N/A')""",
                         name_long='!![en]Stay Caption')
        tbl.formulaColumn('is_current', """$check_in_date <= :env_workdate AND $check_out_date >= :env_workdate""",
                         dtype='B', name_long='!![en]Is Current', _addClass='current_stay')
        #tbl.joinColumn('group_leader_id', name_long='!![en]Group Leader').relation('host.guest.id',
        #                cnd='@group_leader_id.stay_id=$id AND @group_leader_id.@guest_type_code.is_leader IS TRUE'
        #                ) #DP It doesn't work like this
        tbl.formulaColumn('group_leader_id', select=dict(table='host.guest',
                                                         where='$stay_id=#THIS.id AND $is_group_leader IS TRUE',
                                                         columns='$id', limit=1), name_long='!![en]Group Leader'
                          ).relation('host.guest.id', one_one='*')
        tbl.aliasColumn('group_leader_name', '@group_leader_id.full_name',
                       name_long='!![en]Group Leader Name')
        tbl.pyColumn('checkin_url', required_columns='$id')
        tbl.pyColumn('checkin_url_qrcode', required_columns='$id')

    def pyColumn_checkin_url(self,record,field):
        return self.db.application.site.externalUrl('/host/online_checkin',stay_id=record['id'])
    
    def pyColumn_checkin_url_qrcode(self,record,field):
        extUrl = self.db.application.site.externalUrl('/host/online_checkin',stay_id=record['id'])
        extQrcode = self.db.application.site.externalUrl(f'/_tools/qrcode?text={extUrl}')
        return f'<img class="img_qrcode" src="{extQrcode}"/>'