#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
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
        return 'check_in_date DESC'

    def th_query(self):
        return dict(column='group_leader_name', op='contains', val='')
    
    def th_top_custom(self, top):
        top.slotToolbar('5,sections@period,*', childname='upper', _position='<bar')
        
    def th_sections_period(self):
        return [dict(code='future', caption='!![en]Future Stays', condition='$check_in_date >= :env_workdate'),
                dict(code='past', caption='!![en]Past Stays', condition='$check_out_date < :env_workdate')]


class ViewFromFacility(View):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('check_in_date', width='10em', name='!![en]Check-in')
        r.fieldcell('check_out_date', width='10em', name='!![en]Check-out')
        r.fieldcell('nights', width='8em')
        r.fieldcell('group_leader_name', width='auto', name='!![en]Group Leader')
        
    
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
        return dict(dialog_height='500px', dialog_width='800px', modal=True)
