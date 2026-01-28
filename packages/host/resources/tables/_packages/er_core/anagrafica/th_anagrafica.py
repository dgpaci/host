# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent


class FormFacility(BaseComponent):
    py_requires='er_core_component'
    
    def th_form(self, form):
        form.record.anagraficaPane(linkerBar=False,datapath=None,
                                   tipo_anagrafica='societa',
                                   excludeList=['titolo', 'consensi_email', 'fax', 'voip', 'chat','cellulare', 
                                                'rea_provincia', 'rea', 'codice_univoco'], 
                                   abilitaUtenzaEsterna=False)