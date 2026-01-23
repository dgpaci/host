#!/usr/bin/env python
# encoding: utf-8

class Menu(object):
    """Menu configuration for Host Management package"""

    def config(self, root, **kwargs):
        """Configure menu structure"""
        host = root.branch("Host Management", tags="host")

        # Master data section
        anagrafica = host.branch("Master Data", tags="masterdata")
        anagrafica.thpage("Facilities", table="host.facility")
        anagrafica.thpage("Facility Types", table="host.facility_type")
        anagrafica.thpage("Guests", table="host.guest")
        anagrafica.thpage("Guest Types", table="host.guest_type")
        anagrafica.thpage("Document Types", table="host.document_type")
        anagrafica.thpage("Tourist Tax Rates", table="host.tourist_tax")

        # Operations section
        operations = host.branch("Operations", tags="operations")
        operations.thpage("Stays", table="host.stay")
