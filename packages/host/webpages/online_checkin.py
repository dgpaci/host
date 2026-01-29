#!/usr/bin/env python
# encoding: utf-8

"""Online Check-in webpage for guests"""

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = 'public:Public,th/th:TableHandler'

    def main_root(self, root, stay_id=None, **kwargs):
        """Main entry point for online check-in"""
        if not stay_id:
            root.div("!![en]Invalid check-in link", _class='error_message')
            return

        self.stay_id = stay_id
        bc = root.borderContainer(datapath='online_checkin', height='100%', padding='10px')
        self.pageHeader(bc.contentPane(region='top', height='40px', _class='checkin_header'))
        self.pageCenter(bc.contentPane(region='center'))
        
    def pageHeader(self, pane):    
        pane.h3("!![en]Online Check-in", margin_top=0)
        pane.div("!![en]Please complete your information and add your companions")

    def pageCenter(self, pane): 
        pane.thFormHandler(
            table='host.stay',
            startKey=self.stay_id,
            formResource='FormOnlineCheckin', 
            showtoolbar=False)

    @public_method
    def addGuest(self, stay_id=None, is_adult=None):
        """Add a new guest (adult or child) and return its id"""
        if not stay_id:
            return None

        guest_type_code = '19'  # FAMILY_MEMBER

        # Create minimal anagrafica record
        anagrafica_tbl = self.db.table('er_core.anagrafica')
        new_anagrafica = anagrafica_tbl.newrecord()
        anagrafica_tbl.insert(new_anagrafica)

        # Create new guest record
        guest_tbl = self.db.table('host.guest')
        new_guest = guest_tbl.newrecord(
            stay_id=stay_id,
            guest_type_code=guest_type_code,
            anagrafica_id=new_anagrafica['id']
        )

        guest_tbl.insert(new_guest)
        self.db.commit()

        return new_guest['id']

    @public_method
    def checkGuestLimits(self, stay_id=None):
        """Check if can add more adults or children"""
        if not stay_id:
            return {'can_add_adult': False, 'can_add_child': False}

        stay = self.db.table('host.stay').record(pkey=stay_id).output('dict')
        if not stay:
            return {'can_add_adult': False, 'can_add_child': False}

        max_adults = stay.get('adults_count', 0)
        max_children = stay.get('children_count', 0)

        # Count current guests (excluding leader)
        guests = self.db.table('host.guest').query(
            where='$stay_id=:stay_id AND $is_group_leader IS NOT TRUE',
            stay_id=stay_id
        ).fetch()

        # For now count all as adults (we'll improve this with age or guest_type)
        current_adults = len(guests)
        current_children = 0

        return {
            'can_add_adult': current_adults < max_adults,
            'can_add_child': current_children < max_children,
            'current_adults': current_adults,
            'current_children': current_children
        }
