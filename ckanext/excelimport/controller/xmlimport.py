"""Contain XML import controller."""
import ckan.lib.base as base
import ckan.lib.helpers as h
from ckan.lib.munge import munge_title_to_name
from ckan.common import request, c, _
import ckan.model as model
from ckan.logic import (ValidationError, NotAuthorized,
                        NotFound, check_access)
from ckan.logic.validators import package_id_or_name_exists
import ckan.lib.navl.dictization_functions as df
import ckan.plugins.toolkit as tk
import xml.etree.ElementTree as et

from ckanext.excelimport import XML_MAP
from ckanext.excelimport.helpers import get_helpers

abort = base.abort
Invalid = df.Invalid


class XMLImportController(base.BaseController):
    """Controller that provides seed datasets import from ISO19115 XML files."""

    def run_create(self, context, data_dict):
        """Dataset creating proccess."""
        data_dict['name'] = munge_title_to_name(
            data_dict['title']
        )
        try:
            package_id_or_name_exists(data_dict['name'], context)
        except Invalid:
            pass
        else:
            counter = 0

            while True:
                name = '{0}-{1}'.format(data_dict['name'], counter)
                try:
                    package_id_or_name_exists(name, context)
                except Invalid:
                    data_dict['name'] = name
                    break
                counter += 1

        result = self.create_dataset(
            context,
            data_dict,
        )

        if result:
            h.flash_success('Dataset was created!')

    def import_from_xml(self):
        """Method that renders the form and receive submition of the form."""
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user or c.author,
            'for_view': True,
            'auth_user_obj': c.userobj
        }

        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create package'))
        except NotFound:
            abort(404, _('Dataset not found'))

        if request.method == 'POST':

            try:
                xml_file = request.params.get('dataset_xml').filename
                get_helpers.get('validate_file_xml')(xml_file)
            except ValidationError, e:
                h.flash_error(e.error_dict['message'])
            except AttributeError, e:
                h.flash_error('Upload field is empty')
            else:
                xml = request.params.get('dataset_xml').file
                tree = et.parse(xml).getroot()
                data_dict = {}
                get_helpers.get('prepare_dict_from_xml')(
                    tree,
                    XML_MAP,
                    data_dict
                )

                # XML gives us only org title, not name
                data_dict['owner_org'] = munge_title_to_name(
                    data_dict['owner_org']
                )

                if not data_dict.get('id', False):
                    self.run_create(
                        context,
                        data_dict
                    )
                else:
                    pkg = tk.get_action('package_show')(
                        None,
                        {'id': data_dict['id']}
                    )
                    if pkg:
                        h.flash_error('Dataset with id {0} exists'.format(data_dict['id']))
                    else:
                        del data_dict['id']
                        self.run_create(
                            context,
                            data_dict
                        )

        return base.render('snippets/import-from-xml.html')

    def create_dataset(self, context, data_dict):
        """Create dataset with resources (if it has any)."""
        try:
            ds = tk.get_action('package_create')(context, data_dict)

            return ds
        except ValidationError, e:
            h.flash_error(e.error_dict)
