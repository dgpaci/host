#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent

class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('full_name', width='25em', name='Name')
        r.fieldcell('birth_date', width='10em', name='Birth Date')
        r.fieldcell('birth_place', width='20em', name='Birth Place')
        r.fieldcell('citizenship', width='10em')
        r.fieldcell('document_type_description', width='15em', name='Document')
        r.fieldcell('document_number', width='100%', name='Doc. Number')
        return struct

    def th_order(self):
        return 'surname, name'

    def th_query(self):
        return dict(column='surname', op='contains', val='')

class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()

        # Top section - main data
        top = bc.contentPane(region='top', datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')

        # Guest registry link
        fb.field('anagrafica_id', width='40em', colspan=2,
                auxColumns='$surname,$name,$birth_date,$citizenship',
                hasDownArrow=True)

        # Document information section
        fb.div('Document Information', colspan=2, font_weight='bold',
              margin_top='10px', margin_bottom='5px')
        fb.field('document_type_id', width='25em')
        fb.field('document_number', width='25em')
        fb.field('document_issued_by', width='25em')
        fb.field('document_issue_date', width='12em')
        fb.field('document_expiry_date', width='12em')

        # Center section - related stays
        center = bc.tabContainer(region='center', margin='2px')
        stays_tab = center.contentPane(title='Stays')
        stays_tab.dialogTableHandler(relation='@guest_stays',
                                     viewResource='ViewFromGuest')

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='800px')

class ViewFromGuest(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('facility_name', width='25em', name='Facility')
        r.fieldcell('stay_check_in', width='10em', name='Check-in')
        r.fieldcell('stay_check_out', width='10em', name='Check-out')
        r.fieldcell('stay_nights', width='8em', name='Nights')
        r.fieldcell('is_group_leader', width='8em', name='Leader')
        r.fieldcell('tax_amount', width='10em', name='Tax', dtype='N')
        return struct

    def th_order(self):
        return 'stay_check_in DESC'
