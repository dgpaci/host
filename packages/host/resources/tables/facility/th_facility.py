#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent


class View(BaseComponent):
    def th_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('name', width='30em')
        r.fieldcell('facility_type_description', width='15em', name='!![en]Type')
        r.fieldcell('comune_denominazione', width='20em', name='!![en]Municipality')
        return struct

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')
    
    def th_top_custom(self, top):
        top.slotToolbar('5,sections@municipalities,*', childname='upper', _position='<bar')

    def th_sections_municipalities(self):
        municipalities = [x['municipality'] for x in self.db.table('host.facility').query(
                                                            where='$municipality IS NOT NULL', 
                                                            columns='$municipality', distinct=True,
                                                            addPkey=False).fetch()]
        return [dict(code=muni, caption=muni, condition=f"$municipality = '{muni}'") for muni in municipalities
                if municipalities]
        
        
class Form(BaseComponent):
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.borderContainer(region='top', datapath='.record', height='110px')
        fb = top.contentPane(region='center').formlet(cols=2, border_spacing='4px')
        fb.field('name', colspan=2)
        fb.field('facility_type_code', hasDownArrow=True)
        fb.field('max_beds')

        top.contentPane(region='right', width='400px').linkerBox('anagrafica_id',
                                                                 formResource='FormFacility',
                                                                 dialog_width='700px',
                                                                 dialog_height='450px')

        # Bottom section for related stays
        center = bc.tabContainer(region='center', margin='2px')
        stays_tab = center.contentPane(title='!![en]Stays')
        stays_tab.dialogTableHandler(relation='@stays',
                                     viewResource='ViewFromFacility',
                                     formResource='FormFromFacility')

    def th_options(self):
        return dict(dialog_height='500px', dialog_width='700px')
