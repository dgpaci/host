#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    css_requires='host'
    
    def th_hiddencolumns(self):
        return '$is_current'
    
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('facility_name', width='25em', name='!![en]Facility')
        r.fieldcell('check_in_date', width='10em', name='!![en]Check-in')
        r.fieldcell('check_out_date', width='10em', name='!![en]Check-out')
        r.fieldcell('nights', width='8em')
        r.fieldcell('arrival_time', width='10em', name='!![en]Arrival')
        r.fieldcell('flight_number', width='12em', name='!![en]Flight')
        r.fieldcell('group_leader_name', width='auto', name='!![en]Group Leader')

    def th_order(self):
        return 'check_in_date:a'

    def th_query(self):
        return dict(column='group_leader_name', op='contains', val='')
    
    def th_top_custom(self, top):
        top.slotToolbar('5,sections@period,*', childname='upper', _position='<bar')
        
    def th_sections_period(self):
        return [dict(code='future', caption='!![en]Future Stays', condition='$check_out_date >= :env_workdate'),
                dict(code='past', caption='!![en]Past Stays', condition='$check_out_date < :env_workdate')]


class ViewFromFacility(View):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('check_in_date', width='10em', name='!![en]Check-in')
        r.fieldcell('check_out_date', width='10em', name='!![en]Check-out')
        r.fieldcell('nights', width='8em')
        r.fieldcell('group_leader_name', width='auto', name='!![en]Group Leader')
        r.cell('copyurl',calculated=True,name='!![en]Copy',cellClasses='cellbutton',
                    format_buttonclass='copy iconbox', width='3em',
                    format_isbutton=True,
                    format_onclick="""
            var row = this.widget.rowByIndex($1.rowIndex);
            var external_url = row.checkin_url;
            genro.textToClipboard(external_url,_T('Link copiato'));
            """)
        r.fieldcell('checkin_url', name='!![en]Link', width='2.5em',
               template='<a href="$checkin_url" target="_blank"><img src="/_rsrc/common/css_icons/svg/16/link_connected.svg" height="13px"/></a>')
    
    
class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.stayInformations(bc.contentPane(region='top', height='130px', datapath='.record'))
        
        center = bc.tabContainer(region='center', margin='2px')
        self.guestsTab(center.contentPane(title='!![en]Guests'))
        self.exportTab(center)

    def stayInformations(self, pane):
        fb = pane.formlet(cols=4, border_spacing='4px')
        fb.field('facility_id', width='40em', colspan=4, hasDownArrow=True)
        fb.field('check_in_date', width='12em')
        fb.field('check_out_date', width='12em')
        fb.field('arrival_time', width='10em')
        fb.field('flight_number', width='15em')
        
        fb.field('adults_count', width='4em')
        fb.field('children_count', width='4em')
        fb.field('safe_code', width='8em')
        
    def guestsTab(self, guests_tab):
        guests_tab.dialogTableHandler(relation='@guests',
                                      viewResource='ViewFromStay',
                                      formResource='FormFromStay')
        
    def exportTab(self, center):
        export_tab = center.contentPane(title='!![en]Export Police Report')
        export_fb = export_tab.div(margin='10px')
        export_fb.button('!![en]Export TXT for Police',
                        fire='.export_police_report',
                        action='this.publishSelection("export_police_report");')

    def th_options(self):
        return dict(dialog_height='600px', dialog_width='900px')


class FormFromFacility(BaseComponent):
    
    def th_form(self, form):
        bc = form.center.borderContainer()
        self.stayInformations(bc.contentPane(region='top', height='100px', datapath='.record'))
        
        center = bc.tabContainer(region='center', margin='2px')
        self.guestsTab(center.contentPane(title='!![en]Guests'))

    def stayInformations(self, pane):
        fb = pane.formlet(cols=4, border_spacing='4px')
        fb.field('check_in_date', width='12em')
        fb.field('check_out_date', width='12em')
        fb.field('arrival_time', width='10em')
        fb.field('flight_number', width='15em')
        
        fb.field('adults_count', width='4em')
        fb.field('children_count', width='4em')
        fb.field('safe_code', width='8em')
        
    def guestsTab(self, guests_tab):
        guests_tab.dialogTableHandler(relation='@guests',
                                      viewResource='ViewFromStay',
                                      formResource='FormFromStay')
        
    def th_options(self):
        return dict(dialog_height='500px', dialog_width='800px')


class FormOnlineCheckin(BaseComponent):
    """Form for online check-in webpage"""
    py_requires = 'host_component:HostComponent'
    css_requires = 'host'

    def th_form(self, form):
        bc = form.center.borderContainer()
        self.stayInfo(bc.contentPane(region='top', datapath='.record'))
        self.guestForm(bc.contentPane(region='center'))
        self.guestsNavigation(bc.contentPane(region='bottom', height='70px'))

    def stayInfo(self, pane):
        box = pane.styledBox(title='!![en]Stay Information', color_variant='blue')
        self._stayInfoFields(box)

    def _stayInfoFields(self, box):
        fb = box.formlet(cols=4, border_spacing='8px')
        fb.field('facility_name', lbl='!![en]Facility', readOnly=True, colspan=4)
        fb.field('check_in_date', lbl='!![en]Check-in', readOnly=True)
        fb.field('check_out_date', lbl='!![en]Check-out', readOnly=True)
        fb.field('adults_count', lbl='!![en]Adults', readOnly=True)
        fb.field('children_count', lbl='!![en]Children', readOnly=True)
        
    def guestForm(self, pane):
        th = pane.thFormHandler(table='host.guest',
                          formResource='FormCheckIn',
                          _class='pbl_roundedGroup',
                          datapath='#FORM.guests',
                          showtoolbar=False)
        pane.dataController("""frm.goToRecord(group_leader_id);""", 
                          group_leader_id='^#FORM.record.group_leader_id', 
                          frm=th.js_form,
                          _virtual_columns='group_leader_id', 
                          _fired='^#FORM.controller.loaded',
                          _delay=50)

    def guestsNavigation(self, pane):
        self._guestsFormulas(pane)
        box = pane.styledBox(color_variant='purple')
        self._guestsNavigationBar(box)

    def _guestsFormulas(self, pane):
        pane.dataFormula('add_adults_enabled', "current_adults < adults_count?true:false",
                         current_adults='^.current_adults', adults_count='^#FORM.record.adults_count', _onStart=True)
        pane.dataFormula('add_children_enabled', "add_adults_enabled?false:(current_children < children_count?true:false)",
                         current_children='^.current_children', children_count='^#FORM.record.children_count')

    def _guestsNavigationBar(self, box):
        bar = box.slotToolbar('5,adults,children,*,add_adult,add_child,5')
        self._guestsCounters(bar)
        self._addGuestButtons(bar)

    def _guestsCounters(self, bar):
        adfb = bar.adults.formbuilder(cols=2)
        adfb.div("^.current_adults", lbl="!![en]Adults:", font_weight='bold')
        adfb.div("^.adults_count", lbl='/', font_weight='bold')

        chfb = bar.children.formbuilder(cols=2)
        chfb.div("^.current_children", lbl="!![en]Children:", font_weight='bold')
        chfb.div("^.children_count", lbl='/', font_weight='bold')

    def _addGuestButtons(self, bar):
        bar.add_adult.slotButton('!![en]Add Adult',
                 action="""
                     var stay_id = GET .id;
                     genro.serverCall('addGuest', {stay_id: stay_id, is_adult: true}, function(guest_id) {
                         if (guest_id) {
                             SET .guests_changed = new Date();
                             genro.wdgById('guests_handler').widget.openRecord(guest_id);
                         }
                     });
                 """,
                 hidden='^.add_adults_enabled?=!#v')

        bar.add_child.slotButton('!![en]Add Child',
                 action="""
                     var stay_id = GET .id;
                     genro.serverCall('addGuest', {stay_id: stay_id, is_adult: false}, function(guest_id) {
                         if (guest_id) {
                             SET .guests_changed = new Date();
                             genro.wdgById('guests_handler').widget.openRecord(guest_id);
                         }
                     });
                 """,
                 hidden='^.add_children_enabled?=!#v')

    def th_options(self):
        return dict(dialog_height='600px', dialog_width='900px')
