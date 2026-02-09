#!/usr/bin/env python
# encoding: utf-8

"""Online Check-in webpage for guests"""

class GnrCustomWebPage(object):
    py_requires = 'public:Public,th/th:TableHandler'

    def main_root(self, root, stay_id=None, **kwargs):
        """Main entry point for online check-in"""
        if not stay_id:
            root.div("!![en]Invalid check-in link", _class='error_message')
            return

        self.stay_id = stay_id
        bc = root.borderContainer(datapath='online_checkin', height='100%', padding='10px')
        bc.contentPane(region='center').thFormHandler(
            table='host.stay',
            startKey=self.stay_id,
            formResource='FormOnlineCheckin', 
            showtoolbar=False)
