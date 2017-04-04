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

from ckanext.excelimport import (
    XML_MAP,
    XML_RESOURCE_MAP,
    NAMESPACES
)
from ckanext.excelimport.helpers import get_helpers

import xml.etree.ElementTree as et
import re


abort = base.abort
Invalid = df.Invalid


class XMLImportController(base.BaseController):
    """Controller that provides seed datasets import from ISO19115 XML files."""

    def run_create(self, context, data_dict, tree):
        """Dataset creating proccess."""
        try:
            data_dict['name'] = munge_title_to_name(
                data_dict['title']
            )
        except TypeError:
            raise ValidationError({'message': 'Invalid XML file was provided'})
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
            tree
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
                if data_dict['owner_org']:
                    org_title = re.sub(
                        r'\([^)]*\)',
                        '',
                        data_dict['owner_org']
                    )
                    data_dict['owner_org'] = munge_title_to_name(
                        org_title.strip()
                    )

                if not data_dict.get('id', False):
                    try:
                        self.run_create(
                            context,
                            data_dict,
                            tree
                        )
                    except ValidationError, e:
                        h.flash_error(e.error_dict['message'])
                else:
                    try:
                        package_id_or_name_exists(data_dict['id'], context)
                        h.flash_error('Dataset with id {0} exists'.format(
                            data_dict['id'])
                        )
                    except Invalid:
                        del data_dict['id']
                        try:
                            self.run_create(
                                context,
                                data_dict,
                                tree
                            )
                        except ValidationError, e:
                            h.flash_error(e.error_dict['message'])

        return base.render('snippets/import-from-xml.html')

    def create_dataset(self, context, data_dict, tree):
        """Create dataset with resources (if it has any)."""
        try:
            ds = tk.get_action('package_create')(context, data_dict)
            resource_path = tree.find(
                XML_RESOURCE_MAP['resource_location'],
                NAMESPACES
            )
            resource_items = resource_path.findall(
                XML_RESOURCE_MAP['resource_item'],
                NAMESPACES
            )
            resource_formats = tree.findall(
                XML_RESOURCE_MAP['resource_formats']['formats_path'],
                NAMESPACES
            )

            if resource_items:
                self.create_resource(
                    context,
                    ds,
                    resource_items,
                    resource_formats
                )

            return ds
        except ValidationError, e:
            h.flash_error(e.error_dict)

    def create_resource(self, context, data_dict, resources, formats):
        """Create resource with file source or url source."""
        for index, resource in enumerate(resources):
            resource_from = resource.find(
                XML_RESOURCE_MAP['resource_data']['url'],
                NAMESPACES
            ).text
            resource_title = resource.find(
                XML_RESOURCE_MAP['resource_data']['name'],
                NAMESPACES
            ).text
            resource_desc = resource.find(
                XML_RESOURCE_MAP['resource_data']['description'],
                NAMESPACES
            ).text
            resource_format = formats[index].find(
                XML_RESOURCE_MAP['resource_formats']['formats_data']['format'],
                NAMESPACES
            ).text

            if resource_from:
                tk.get_action('resource_create')(context, {
                    'package_id': data_dict['id'],
                    'url': resource_from,
                    'name': resource_title,
                    'description': resource_desc,
                    'format': resource_format
                })
