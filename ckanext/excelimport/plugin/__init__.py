import ckan.plugins as plugins
import ckan.plugins.toolkit as tk


if tk.check_ckan_version("2.9"):
    from ckanext.excelimport.plugin.flask_plugin import MixinPlugin
else:
    from ckanext.excelimport.plugin.pylons_plugin import MixinPlugin

class ExcelImportPlugin(MixinPlugin, plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, '../templates')
        tk.add_public_directory(config_, '../public')
        tk.add_resource('../fanstatic', 'seeding')

