"""Contain XML import controller."""
import ckan.lib.base as base
import ckan.lib.helpers as h
from ckan.lib.munge import munge_title_to_name
from ckan.common import request, c, _
import ckan.model as model
from ckan.logic import (ValidationError, NotAuthorized,
                        NotFound, check_access)
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


class XMLUpdateController(base.BaseController):
    """Controller that provides seed datasets import from ISO19115 XML files."""

    def update_from_xml(self, id):
        """Method that renders the form and receive submition of the form."""
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user or c.author,
            'for_view': True,
            'auth_user_obj': c.userobj
        }

        try:
            check_access('package_update', context, {'id': id})
            c.pkg_dict = tk.get_action('package_show')(context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))
        c.show_org = False

        if request.method == 'POST':

            try:
                xml_file = request.params.get('dataset_xml').filename
                owner_org = request.params.get('owner_org', None)
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
                if owner_org is None:
                    if data_dict['owner_org']:
                        org_title = re.sub(
                            r'\([^)]*\)',
                            '',
                            data_dict['owner_org']
                        )
                        data_dict['owner_org'] = munge_title_to_name(
                            org_title.strip()
                        )
                else:
                    data_dict['owner_org'] = owner_org

                if not data_dict.get('id', False):
                    h.flash_error('Metadata sheet must contain package id field.')
                if data_dict['id'] not in [c.pkg_dict['id'], c.pkg_dict['name']]:
                    error_msg = (
                        '<p>XML fileIdentifier field is incorrect.</p>'
                        '<i>XML fileIdentifier id can be dataset\'s name or id.</i>'
                        '<br/>XML fileIdentifier id: {0}<br/>'
                        'datatest id: {1}<br/>'
                        'dataset name: {2}'
                    ).format(
                        data_dict['id'],
                        c.pkg_dict['id'],
                        c.pkg_dict['name']
                    )
                    h.flash_error(error_msg, True)
                else:
                    try:
                        result = self.update_dataset(
                            context,
                            data_dict,
                            tree,
                            c.pkg_dict
                        )
                        if result:
                            h.flash_success('Dataset was updated!')
                    except NotAuthorized, e:
                        c.show_org = True
                        h.flash_error(e)
                    except ValidationError, e:
                        if "owner_org" in e.error_dict:
                            c.show_org = True
                        h.flash_error(e.error_dict)

        return base.render('snippets/update-from-xml.html')

    def update_dataset(self, context, data_dict, tree, pkg_dict):
        """Create dataset with resources (if it has any)."""
        try:
            pkg_dict.update(data_dict)
            del pkg_dict['resources']
            ds = tk.get_action('package_update')(context, pkg_dict)
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
        except ValidationError as e:
            raise e

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
