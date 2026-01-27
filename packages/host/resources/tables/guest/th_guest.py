#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('facility_name', width='20em', name='!![en]Facility')
        r.fieldcell('stay_check_in', width='10em', name='!![en]Check-in')
        r.fieldcell('stay_check_out', width='10em', name='!![en]Check-out')
        r.fieldcell('full_name', width='25em', name='!![en]Guest')
        r.fieldcell('guest_type_description', width='15em', name='!![en]Type')
        r.fieldcell('tax_amount', width='100%', name='!![en]Tax', dtype='N')
        return struct

    def th_order(self):
        return 'stay_check_in DESC, guest_type_code'

    def th_query(self):
        return dict(column='surname', op='contains', val='')


class ViewFromStay(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('full_name', width='20em', name='!![en]Guest')
        r.fieldcell('guest_type_description', width='10em', name='!![en]Type')
        r.fieldcell('birth_date', width='6em', name='!![en]Birth Date')
        r.fieldcell('tax_amount', width='10em', name='!![en]Tax Amount', dtype='N', totalize=True)
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
        fb.field('guest_type_code', width='30em', hasDownArrow=True)
        fb.field('tourist_tax_code', width='40em', colspan=2, hasDownArrow=True)
        fb.field('tax_amount', width='15em', readonly=True)

        # Document information section
        fb.div('!![en]Document Information', colspan=2, font_weight='bold',
              margin_top='10px', margin_bottom='5px')
        fb.field('document_type_code', width='25em')
        fb.field('document_number', width='25em')
        fb.field('document_issued_by', width='25em')
        fb.field('document_issue_date', width='12em')
        fb.field('document_expiry_date', width='12em')

    def th_options(self):
        return dict(dialog_height='450px', dialog_width='800px')
    

class FormFromStay(BaseComponent):
    
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        self.guestPersonalDetails(bc.contentPane(region='top', datapath='.@anagrafica_id'))
        self.guestInformations(bc.contentPane(region='center'))
    
    def guestPersonalDetails(self, pane):
        fl = pane.formlet(cols=4, table='er_core.anagrafica')
        fl.field('nome', colspan=2, validate_notnull=True)
        fl.field('cognome', colspan=2, validate_notnull=True)
        fl.field('sesso', validate_notnull=True)
        fl.field('data_nascita', validate_notnull=True)
        fl.field('luogo_nascita')
        fl.field('nazione_nascita')
        fl.field('cittadinanza')
        fl.field('nazione', lbl='!![en]Country of Residence', validate_notnull=True)
        fl.field('provincia', hidden='^.nazione?=#v!="IT"',
                                lbl='!![en]Province of Residence',
                                validate_notnull='^.@guest_type_code.is_leader')
                 
    def guestInformations(self, pane):
        fl = pane.formlet(cols=2)

        # Guest type and tax
        fl.field('guest_type_code', width='30em', hasDownArrow=True)
        fl.field('tourist_tax_code', width='40em', colspan=2, hasDownArrow=True)
        fl.field('tax_amount', width='15em', readonly=True)

        # Document information section
        fl.div('!![en]Document Information', colspan=2, font_weight='bold',
                    margin_top='10px', margin_bottom='5px')
        fl.field('document_type_code', width='25em')
        fl.field('document_number', width='25em')
        fl.field('document_issued_by', width='25em')
        fl.field('document_issue_date', width='12em')
        fl.field('document_expiry_date', width='12em')

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')