#!/usr/bin/env python
# encoding: utf-8

class Menu(object):
    """Menu configuration for Host Management package"""

    def config(self, root, **kwargs):
        """Configure menu structure"""
        host = root.branch("!![en]Host Management")

        # Master data section
        anagrafica = host.branch("!![en]Master Data")
        anagrafica.thpage("!![en]Facilities", table="host.facility")
        anagrafica.thpage("!![en]Guests", table="host.guest")
        anagrafica.thpage("!![en]Tourist Tax Rates", table="host.tourist_tax")

        # Operations section
        operations = host.branch("!![en]Operations")
        operations.thpage("!![en]Stays", table="host.stay")
        
        root.lookupBranch('!![en]Settings', pkg='host')
