# -*- coding: utf-8 -*-

import ckan.plugins as p


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes

    def before_map(self, map):
        with SubMapper(
            map,
            controller="ckanext.excelimport.controller.excelimport:ExcelImportController",
            path_prefix='/dashboard'
        ) as m:
            m.connect('excelimport.import_from_zip', '/import-from-zip', action='import_from_zip')
        with SubMapper(
            map,
            controller="ckanext.excelimport.controller.excelupdate:ExcelUpdateController",
            path_prefix='/dataset'
        ) as m:
            m.connect('excelimport.dataset_update_zip', '/update-from-zip/{id}', action='update_from_zip')

        return map
