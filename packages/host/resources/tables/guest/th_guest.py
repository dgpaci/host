#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('facility_name', width='20em', name='Facility')
        r.fieldcell('stay_check_in', width='10em', name='Check-in')
        r.fieldcell('stay_check_out', width='10em', name='Check-out')
        r.fieldcell('full_name', width='25em', name='Guest')
        r.fieldcell('guest_type_description', width='15em', name='Type')
        r.fieldcell('tax_amount', width='100%', name='Tax', dtype='N')
        return struct

    def th_order(self):
        return 'stay_check_in DESC, guest_type_code'

    def th_query(self):
        return dict(column='surname', op='contains', val='')


class ViewFromStay(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('full_name', width='20em', name='Guest')
        r.fieldcell('guest_type_description', width='10em', name='Type')
        r.fieldcell('birth_date', width='6em', name='Birth Date')
        r.fieldcell('tax_amount', width='10em', name='Tax Amount', dtype='N', totalize=True)
        return struct

    def th_order(self):
        return 'guest_type_code, surname'
    
    
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

        # Guest type and tax
        fb.field('guest_type_id', width='30em', hasDownArrow=True)
        fb.field('tourist_tax_id', width='40em', colspan=2, hasDownArrow=True)
        fb.field('tax_amount', width='15em', readonly=True)

        # Document information section
        fb.div('Document Information', colspan=2, font_weight='bold',
              margin_top='10px', margin_bottom='5px')
        fb.field('document_type_id', width='25em')
        fb.field('document_number', width='25em')
        fb.field('document_issued_by', width='25em')
        fb.field('document_issue_date', width='12em')
        fb.field('document_expiry_date', width='12em')

    def th_options(self):
        return dict(dialog_height='450px', dialog_width='800px')
    

class FormFromStay(BaseComponent):
    py_requires="er_core_component:AnagraficaComponent"
    
    def th_form(self, form):
        bc = form.center.borderContainer()
        bc.contentPane(region='top', height='350px').anagraficaPane(
                                tipo_anagrafica='persona',
                                linkerBar=False,
                                title='Guest Information',
                                saveIndirizzoEsteso=False,
                                excludeList=['fax','voip','www','chat','partita_iva'],
                                fb_kwargs=dict(cols=2))
        self.guestInformations(bc.contentPane(region='center', datapath='.record'))
    
    def guestInformations(self, pane):
        fl = pane.formlet(cols=2)

        # Guest type and tax
        fl.field('guest_type_id', width='30em', hasDownArrow=True)
        fl.field('tourist_tax_id', width='40em', colspan=2, hasDownArrow=True)
        fl.field('tax_amount', width='15em', readonly=True)

        # Document information section
        fl.div('Document Information', colspan=2, font_weight='bold',
                    margin_top='10px', margin_bottom='5px')
        fl.field('document_type_id', width='25em')
        fl.field('document_number', width='25em')
        fl.field('document_issued_by', width='25em')
        fl.field('document_issue_date', width='12em')
        fl.field('document_expiry_date', width='12em')

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')