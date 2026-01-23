#!/usr/bin/env python
# encoding: utf-8

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

class Table(GnrDboTable):
    """Base table class for host package"""
    pass
