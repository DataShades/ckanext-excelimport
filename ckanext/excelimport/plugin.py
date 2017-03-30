import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from routes.mapper import SubMapper


class ExcelImportPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'seeding')

    # IRouter

    def before_map(self, map):

        # ZIP import
        with SubMapper(
            map,
            controller="ckanext.excelimport.controller.excelimport:ExcelImportController",
            path_prefix='/dashboard'
        ) as m:
            m.connect('import_from_zip', '/import-from-zip', action='import_from_zip')
        with SubMapper(
            map,
            controller="ckanext.excelimport.controller.excelupdate:ExcelUpdateController",
            path_prefix='/dataset'
        ) as m:
            m.connect('dataset_update_zip', '/update-from-zip/{id}', action='update_from_zip')

        # XML import
        with SubMapper(
            map,
            controller="ckanext.excelimport.controller.xmlimport:XMLImportController",
            path_prefix='/dashboard'
        ) as m:
            m.connect('import_from_xml', '/import-from-xml', action='import_from_xml')

        return map
