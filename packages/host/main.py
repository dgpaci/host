#!/usr/bin/env python
# encoding: utf-8
from datetime import date
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    """Host Management Package for accommodation facilities and guest tracking"""

    def config_attributes(self):
        return dict(
            comment='Host Management Package',
            sqlschema='host',
            name_short='Host',
            name_long="Host Management",
            name_full='Host Management System'
        )

    def config_db(self, pkg):
        """Package configuration"""
        pass
    
    def required_packages(self):
        return ['erpyready:er_core']


class Table(GnrDboTable):
    """Base table class for host package"""
    
    def _resolve_comune_from_istat(self, istat_code):
        if not istat_code or not istat_code.isdigit():
            return None, None
        comune_name, prov = self.db.table('glbl.comune').readColumns(
            where='$codice_comune=:code',
            code=istat_code,
            columns='$denominazione,$sigla_provincia'
        )
        comune_name = comune_name or None
        prov = prov or None
        if not comune_name and not prov:
            return None, None
        return comune_name, prov

    def _resolve_country_from_istat(self, istat_code):
        if not istat_code:
            return None
        code = istat_code.strip()
        if not code:
            return None
        if code.isdigit():
            country_code = self.db.table('glbl.nazione').readColumns(
                where='$nmbr=:code OR $nmbrunico=:code',
                code=code,
                columns='$code'
            )
            return country_code or None

        country_code = self.db.table('glbl.nazione').readColumns(
            where='$code=:code OR $code3=:code',
            code=code,
            columns='$code'
        )
        return country_code or None

    def _parse_ddmmyyyy(self, value):
        if not value:
            return None
        try:
            day, month, year = [int(x) for x in value.split('/')]
            return date(year, month, day)
        except Exception:
            return None
