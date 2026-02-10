#!/usr/bin/env python
# encoding: utf-8

from datetime import timedelta
from gnr.app import pkglog as logger

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

        tbl.formulaColumn('current_adults', "COALESCE(#curr_adults, 0)",
                         select_curr_adults=dict(table='host.guest',
                                   where="""$stay_id=#THIS.id AND
                                           @anagrafica_id.data_nascita IS NOT NULL AND
                                           EXTRACT(YEAR FROM AGE(#THIS.check_in_date, @anagrafica_id.data_nascita)) >= 12""",
                                   columns='COUNT(*)'),
                         dtype='I', name_long='!![en]Current Adults')

        tbl.formulaColumn('current_children', "COALESCE(#curr_children, 0)",
                          select_curr_children=dict(table='host.guest',
                                   where="""$stay_id=#THIS.id AND
                                           @anagrafica_id.data_nascita IS NOT NULL AND
                                           EXTRACT(YEAR FROM AGE(#THIS.check_in_date, @anagrafica_id.data_nascita)) < 12""",
                                   columns='COUNT(*)'),
                          dtype='I', name_long='!![en]Current Children')

        tbl.pyColumn('checkin_url', required_columns='$id')
        tbl.pyColumn('checkin_url_qrcode', required_columns='$id')

    def pyColumn_checkin_url(self,record,field):
        return self.db.application.site.externalUrl('/host/online_checkin',stay_id=record['id'])
    
    def pyColumn_checkin_url_qrcode(self,record,field):
        extUrl = self.db.application.site.externalUrl('/host/online_checkin',stay_id=record['id'])
        extQrcode = self.db.application.site.externalUrl(f'/_tools/qrcode?text={extUrl}')
        return f'<img class="img_qrcode" src="{extQrcode}"/>'

    def importer_stays_from_txt(self, reader=None, facility_id=None, **kwargs):
        """
        Import stays + guests from fixed-width trace (170 chars).
        reader: callable returning iterable of rows (string line or dict with key 'line')
        """
        if not facility_id:
            raise Exception('facility_id is required')
        if not reader:
            return dict(inserted=0, errors=['Missing reader'], stay_id=None, guests=[])

        logger.info("Importer start facility_id=%s", facility_id)

        lines = []
        try:
            if hasattr(reader, 'headers'):
                hdrs = getattr(reader, 'headers', None)
                if isinstance(hdrs, (list, tuple)) and len(hdrs) == 1:
                    hdr_line = hdrs[0]
                    if isinstance(hdr_line, str) and len(hdr_line.strip()) >= 168:
                        lines.append(hdr_line)

            for r in reader():
                line = None
                if isinstance(r, str):
                    line = r
                elif hasattr(r, 'get'):
                    line = r.get('line') or r.get('raw') or r.get('record')
                if line is None and hasattr(r, '__getitem__'):
                    try:
                        line = r['line']
                    except Exception:
                        try:
                            line = r[0]
                        except Exception:
                            line = None
                if line is None:
                    line = str(r)
                raw = (line or '').rstrip('\r\n')
                if raw:
                    lines.append(raw)
        finally:
            try:
                if hasattr(reader, 'filecsv') and reader.filecsv:
                    reader.filecsv.close()
            except Exception:
                logger.warning("Importer could not close reader file", exc_info=True)
            try:
                if hasattr(reader, 'close'):
                    reader.close()
            except Exception:
                logger.warning("Importer could not close reader", exc_info=True)

        if not lines:
            logger.warning("Importer empty content facility_id=%s", facility_id)
            return dict(inserted=0, errors=['Empty content'], stay_id=None, guests=[])

        errors = []

        first = lines[0]
        if len(first) < 168:
            return dict(inserted=0, errors=[f"Line 1: invalid length {len(first)}"], stay_id=None, guests=[])

        arrival_date = first[2:12].strip()
        days_of_stay = first[12:14].strip()

        check_in_date = self._parse_ddmmyyyy(arrival_date)
        try:
            nights = int(days_of_stay) if days_of_stay else 0
        except Exception:
            nights = 0

        if not check_in_date:
            logger.error("Importer invalid arrival_date=%s", arrival_date)
            return dict(inserted=0, errors=['Invalid arrival date'], stay_id=None, guests=[])

        check_out_date = check_in_date + timedelta(days=nights or 0)

        stay_id = self.importNewStay(facility_id=facility_id,
                              check_in_date=check_in_date, 
                              check_out_date=check_out_date)

        self.db.table('host.guest').importNewGuests(lines=lines, first=first, stay_id=stay_id)

        self.db.commit()
        
    def importNewStay(self, facility_id=None, check_in_date=None, check_out_date=None, **kwargs):
        stay_record = self.newrecord(
            facility_id=facility_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            assignId=True
        )
        self.insert(stay_record)
        return stay_record.get('id')