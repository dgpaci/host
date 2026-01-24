#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('facility_name', width='25em', name='Facility')
        r.fieldcell('check_in_date', width='10em', name='Check-in')
        r.fieldcell('check_out_date', width='10em', name='Check-out')
        r.fieldcell('nights', width='8em')
        r.fieldcell('arrival_time', width='10em', name='Arrival')
        r.fieldcell('flight_number', width='12em', name='Flight')

        # Show group leader name (calculated via SQL)
        r.fieldcell('group_leader_name', width='100%', name='Group Leader',
                   calculated=True,
                   sql_formula="""(SELECT g.ragione_sociale
                                   FROM host.stay_guest sg
                                   JOIN host.guest gu ON sg.guest_id = gu.id
                                   JOIN erpy_base.anagrafica g ON gu.anagrafica_id = g.id
                                   JOIN host.guest_type gt ON sg.guest_type_id = gt.id
                                   WHERE sg.stay_id = $id AND gt.code IN ('17', '18')
                                   LIMIT 1)""")
        return struct

    def th_order(self):
        return 'check_in_date DESC'

    def th_query(self):
        return dict(column='check_in_date', op='>=', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()

        # Top section - main data
        top = bc.contentPane(region='top', height='160px', datapath='.record')
        fb = top.formbuilder(cols=3, border_spacing='4px')
        fb.field('facility_id', width='40em', colspan=3, hasDownArrow=True)
        fb.field('check_in_date', width='12em')
        fb.field('check_out_date', width='12em')
        fb.field('nights', width='8em', readonly=True)
        fb.field('arrival_time', width='10em')
        fb.field('flight_number', width='15em')
        fb.field('safe_code', width='8em')

        # Center section - guests in this stay
        center = bc.tabContainer(region='center', margin='2px')

        # Tab for stay_guest records
        guests_tab = center.contentPane(title='Guests')
        guests_tab.dialogTableHandler(relation='@stay_guests',
                                      viewResource='ViewFromStay',
                                      formResource='FormFromStay')

        # Tab for police report export
        export_tab = center.contentPane(title='Export Police Report')
        export_fb = export_tab.div(margin='10px')
        export_fb.button('Export TXT for Police',
                        fire='.export_police_report',
                        action='this.publishSelection("export_police_report");')

    def th_options(self):
        return dict(dialog_height='600px', dialog_width='900px')

class ViewFromStay(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('guest_name', width='25em', name='Guest')
        r.fieldcell('guest_type_description', width='15em', name='Type')
        r.fieldcell('guest_birth_date', width='10em', name='Birth Date')
        r.fieldcell('tax_description', width='30em', name='Tax Rate')
        r.fieldcell('tax_amount', width='10em', name='Tax Amount', dtype='N')
        return struct

    def th_order(self):
        return 'guest_type_code, guest_surname'

class FormFromStay(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top', datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('guest_id', width='40em', colspan=2,
                auxColumns='$birth_date,$citizenship',
                hasDownArrow=True)
        fb.field('guest_type_id', width='30em', hasDownArrow=True)
        fb.field('tourist_tax_id', width='40em', colspan=2, hasDownArrow=True)
        fb.field('tax_amount', width='15em', readonly=True)

    def th_options(self):
        return dict(dialog_height='300px', dialog_width='600px')
