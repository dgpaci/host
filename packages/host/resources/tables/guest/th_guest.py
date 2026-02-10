#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

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
        return 'stay_check_in DESC,guest_type_code'

    def th_query(self):
        return dict(column='surname', op='contains', val='')


class ViewFromStay(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('full_name', width='20em', name='!![en]Guest')
        r.fieldcell('guest_type_description', width='10em', name='!![en]Type')
        r.fieldcell('birth_date', width='6em')
        r.fieldcell('tax_amount', width='10em', name='!![en]Tax Amount', dtype='N', totalize=True)
        return struct

    def th_order(self):
        return 'guest_type_code,surname'


class ViewOnlineCheckin(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('full_name', width='20em', name='!![en]Guest')
        r.fieldcell('guest_type_description', width='10em', name='!![en]Type')
        r.fieldcell('birth_date', width='6em')
        return struct

    def th_order(self):
        return 'guest_type_code,surname'
        
    
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
        fb.field('document_issued_by_provincia', lbl='!![en]Issued By (Province)',
                hidden='^#FORM.record.@anagrafica_id.cittadinanza?=#v!="IT"')
        fb.field('document_issued_by_country', lbl='!![en]Issued By',
                hidden='^#FORM.record.@anagrafica_id.cittadinanza?=#v=="IT"')
        fb.field('document_issue_date', width='12em')
        fb.field('document_expiry_date', width='12em')

    def th_options(self):
        return dict(dialog_height='450px', dialog_width='800px')
    

class FormFromStay(BaseComponent):
    
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        self.guestPersonalDetails(bc.contentPane(region='top', datapath='.@anagrafica_id'))
        self.documentInformations(bc.contentPane(region='center'))
        self.tourismTaxDefinition(bc.contentPane(region='bottom'))
    
    def guestPersonalDetails(self, pane):
        fl = pane.formlet(cols=4, table='er_core.anagrafica')
        fl.div('!![en]Personal Details', colspan=4, font_weight='bold',
                        margin_top='10px', margin_bottom='5px')
        fl.field('nome', colspan=2, validate_notnull=True)
        fl.field('cognome', colspan=2, validate_notnull=True)
        fl.field('sesso', validate_notnull=True, tag='filteringSelect', values='[!![en]M],[!![en]F]')
        fl.field('data_nascita')
        fl.field('luogo_nascita')
        fl.field('nazione_nascita', selected_code='.cittadinanza')
        fl.field('cittadinanza')
        fl.field('nazione', lbl='!![en]Country of Residence', validate_notnull=True)
        fl.field('provincia', hidden='^.nazione?=#v!="IT"',
                                lbl='!![en]Province of Residence')
                 
    def tourismTaxDefinition(self, pane):
        fl = pane.formlet(cols=3)
        fl.div('!![en]Tourism Tax Definition', colspan=3, font_weight='bold',
                        margin_top='10px', margin_bottom='5px')
        fl.field('guest_type_code', hasDownArrow=True)
        fl.field('tourist_tax_code', hasDownArrow=True)
        fl.field('tax_amount', readOnly=True)

    def documentInformations(self, pane):
        fl = pane.formlet(cols=3)
        fl.div('!![en]Document Information', colspan=3, font_weight='bold',
                        margin_top='10px', margin_bottom='5px')
        fl.field('document_type_code', colspan=2)
        fl.field('document_number')
        fl.field('document_issued_by_provincia', lbl='!![en]Issued By (Province)',
                hidden='^#FORM.record.@anagrafica_id.cittadinanza?=#v!="IT"')
        fl.field('document_issued_by_country', lbl='!![en]Issued By',
                hidden='^#FORM.record.@anagrafica_id.cittadinanza?=#v=="IT"')
        fl.field('document_issue_date')
        fl.field('document_expiry_date')

    def th_options(self):
        return dict(dialog_height='420px', dialog_width='700px')
        

class FormCheckIn(FormFromStay):
    py_requires = 'host_component:HostComponent'
    css_requires = 'host'

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        self.guestPersonalDetails(bc.contentPane(region='top', datapath='.@anagrafica_id'))
        self.documentInformations(bc.contentPane(region='center'))
        self.tourismTaxDefinition(bc.contentPane(region='bottom'))

    def guestPersonalDetails(self, pane):
        box = pane.styledBox(title='!![en]Personal Details',
                            color_variant='green',
                            linkerBar=dict(table='host.guest',
                                          value='^#FORM.current_guest_id',
                                          condition='$stay_id=:stay_id',
                                          condition_stay_id='=#FORM.record.stay_id',
                                          lbl='!![en]Guest',
                                          width='15em',
                                          hasDownArrow=True))
        self._personalDetailsFields(box)

    def _personalDetailsFields(self, box):
        fl = box.formlet(cols=4, table='er_core.anagrafica', fld_validate_notnull=True)
        fl.field('nome', colspan=2, validate_notnull=True)
        fl.field('cognome', colspan=2, validate_notnull=True)
        fl.field('sesso', tag='filteringSelect', values='M:[!![en]Male],F:[!![en]Female]')
        fl.field('data_nascita', lbl='!![en]D. of Birth', validate_notnull=True)
        fl.field('nazione_nascita', colspan=2, selected_code='.cittadinanza', validate_notnull=True)
        fl.field('luogo_nascita', lbl='!![en]P. of Birth', hidden='^.nazione_nascita?=#v!="IT"', 
                                validate_notnull='^.nazione_nascita?=#v=="IT"')
        fl.field('cittadinanza', colspan=2, validate_notnull=True, 
                                selected_code='#FORM.record.document_issued_by_country')
        fl.field('nazione', lbl='!![en]Country of Residence', colspan=2,validate_notnull=True)
        fl.field('provincia', lbl='!![en]Province', hidden='^.nazione?=#v!="IT"',
                                validate_notnull='^.nazione?=#v=="IT"',
                                selected_sigla='#FORM.record.document_issued_by_provincia')

    def documentInformations(self, pane):
        box = pane.styledBox(title='!![en]Document Information', color_variant='orange')
        self._documentFields(box)

    def _documentFields(self, box):
        fl = box.formlet(cols=3)
        fl.field('document_type_code', colspan=2, validate_notnull='^#FORM.record.is_group_leader')
        fl.field('document_number', lbl='!![en]Number', validate_notnull='^#FORM.record.is_group_leader')
        fl.field('document_issued_by_provincia', lbl='!![en]Issued By',
                hidden='^#FORM.record.@anagrafica_id.cittadinanza?=#v!="IT"',
                validate_notnull='==(is_group_leader && cittadinanza=="IT")',
                is_group_leader='^#FORM.record.is_group_leader',
                cittadinanza='^#FORM.record.@anagrafica_id.cittadinanza',
                hasDownArrow=True)
        fl.field('document_issued_by_country', lbl='!![en]Issued By',
                hidden='^#FORM.record.@anagrafica_id.cittadinanza?=#v=="IT"',
                validate_notnull='==(is_group_leader && cittadinanza!="IT")',
                is_group_leader='^#FORM.record.is_group_leader',
                cittadinanza='^#FORM.record.@anagrafica_id.cittadinanza',
                hasDownArrow=True)
        fl.field('document_issue_date', lbl='!![en]Issue Date')
        fl.field('document_expiry_date', lbl='!![en]Expiry Date')
        
    def tourismTaxDefinition(self, pane):
        box = pane.styledBox(title='!![en]Tourism Tax', color_variant='yellow')
        self._tourismTaxFields(box)
        pane.onDbChanges("""
            var that=this;
            console.log('dbChanges');
            if(dbChanges && guest_id && dbChanges.some(c => c.pkey==guest_id && c.tax_amount!== null && c.dbevent=='U')){
                this.form.reload();
            }
        """, table='host.guest', guest_id='^#FORM.pkey')
        
    def _tourismTaxFields(self, box):
        fl = box.formlet(cols=3)
        fl.field('guest_type_code', hasDownArrow=True)
        fl.field('tourist_tax_code', hasDownArrow=True)
        fl.field('tax_amount', readOnly=True)

    def th_options(self):
        return dict(dialog_height='520px', dialog_width='700px', autoSave=True)
