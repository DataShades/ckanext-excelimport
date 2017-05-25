from ckan.logic import ValidationError
from ckan.common import request
from ckan.lib.uploader import get_storage_path
from dateutil.parser import parse

import shapely.geometry as geo
import cgi
import json
import os

from ckanext.excelimport import (
    FIELD_MAPPING, MAP_TYPES, NAMESPACES
)


def validate_file_ext(zip_file):
    """Validate for .zip file passed into the form."""
    if not zip_file.lower().endswith('.zip'):
        raise ValidationError({'message': 'Please, upload a zip archive'})


def validate_file_xml(xml_file):
    """Validate for .xml file passed into the form."""
    if not xml_file.lower().endswith('.xml'):
        raise ValidationError({'message': 'Please, upload a xml file'})


def prepare_data_dict(data_dict, rows):
    """Parse .xlsx file and pushes data to dict."""
    for row in rows:
        field = row[0].value
        value = row[1].value

        try:
            if field is not None and field in FIELD_MAPPING:
                if FIELD_MAPPING[field] == 'topic' and value:
                    value = value.title()
                if FIELD_MAPPING[field] == 'private':
                    if 'private' in value.lower():
                        value = True
                    else:
                        value = False
                if FIELD_MAPPING[field] == 'map_type' and value:
                    if value in MAP_TYPES:
                        value = MAP_TYPES[value]

                data_dict[FIELD_MAPPING[field]] = value
        except KeyError, e:
            raise e


def prepare_dict_from_xml(tree, xml_map, data_dict):
    """Parse .xml file and pushes data to dict."""
    for key, value in xml_map.iteritems():

        if key == 'tag_string':
            tags = []
            tag_list = tree.find(value['x_value'], NAMESPACES)
            try:
                for tag in tag_list.iterfind(value['x_iter'], NAMESPACES):
                    tags.append(tag.text)
            except AttributeError:
                pass
            data_dict[key] = ','.join(tags)
        elif key == 'private':
            data_dict[key] = True
        elif key == 'spatial':
            try:
                spatial = tree.find(value['x_value'], NAMESPACES)
                data_dict[key] = geo.mapping(geo.box(
                    float(spatial.find(value['x_coords']['west'], NAMESPACES).text),
                    float(spatial.find(value['x_coords']['south'], NAMESPACES).text),
                    float(spatial.find(value['x_coords']['east'], NAMESPACES).text),
                    float(spatial.find(value['x_coords']['north'], NAMESPACES).text),
                ))
                data_dict[key] = json.dumps(data_dict[key])
            except AttributeError:
                data_dict[key] = None
        elif key == 'temporal_extent':
            try:
                temporal_data = tree.find(value['x_value'], NAMESPACES)
                begin = temporal_data.find(value['x_temporal']['begin'], NAMESPACES)
                end = temporal_data.find(value['x_temporal']['end'], NAMESPACES)
                begin_date = parse(begin.text)
                end_date = parse(end.text)

                data_dict[key] = "{0} - {1}".format(
                    begin_date.strftime('%B %Y'),
                    end_date.strftime('%B %Y'),
                )
            except AttributeError:
                data_dict[key] = None
        elif key == 'topic':
            try:
                data_dict[key] = tree.find(value, NAMESPACES).text.title()
            except AttributeError:
                data_dict[key] = None
        elif key == 'update_frequency':
            frequency = tree.find(value, NAMESPACES)
            try:
                data_dict[key] = frequency.text
            except AttributeError:
                data_dict[key] = 'Unknown'
        elif key == 'type':
            data_dict[key] = 'dataset'
        elif key == 'map_type':
            data_dict[key] = ''
        elif key == 'created':
            created_xml = tree.find(value, NAMESPACES)

            if created_xml is not None:
                data_dict[key] = parse(
                    created_xml.text
                )
        else:
            try:
                data_dict[key] = tree.find(value, NAMESPACES).text
            except AttributeError:
                data_dict[key] = None


def prepare_file(content, bytes, source):
    """Prepare FieldStorage for resource create."""
    fs = cgi.FieldStorage(
        fp=bytes,
        headers={
            'content-type': 'multipart/form-data; boundary=resource',
            'content-disposition': 'form-data; name="file"; filename="{0}"'
            .format(source),
            'content-length': len(content)
        },
        environ={'REQUEST_METHOD': 'POST'}
    )
    fs.file = bytes

    return fs


def save_tmp_file(file, filename, user):
    tmp_name = '{0}.tmp'.format(user)
    upload_path = get_storage_path()
    upload_dir = 'excelimport'
    full_path = '{0}/{1}'.format(upload_path, upload_dir)

    if not os.path.exists(full_path):
        os.makedirs(full_path)
    tmp_file = open(
        '{0}/{1}'.format(full_path, tmp_name),
        'wb'
    )
    file.seek(0)
    tmp_file.write(file.read())
    tmp_file.close()

    # add to session
    session = request.environ['beaker.session']
    tmp_dict = {}
    tmp_dict[filename] = tmp_name
    session['excelimport_tmp'] = tmp_dict
    session.save()


def get_tmp_file():
    session = request.environ['beaker.session']

    if 'excelimport_tmp' in session:
        return session['excelimport_tmp']

    return None


def clean_tmp_file():
    upload_path = get_storage_path()
    session = request.environ['beaker.session']

    if 'excelimport_tmp' in session:
        filename, tmp_name = session['excelimport_tmp'].items()[0]
        full_path = '{0}/excelimport/{1}'.format(
            upload_path,
            tmp_name
        )
        if os.path.exists(full_path):
            os.remove(full_path)
        del session['excelimport_tmp']
        session.save()


get_helpers = {
    'validate_file_ext': validate_file_ext,
    'validate_file_xml': validate_file_xml,
    'prepare_data_dict': prepare_data_dict,
    'prepare_dict_from_xml': prepare_dict_from_xml,
    'prepare_file': prepare_file,
    'save_tmp_file': save_tmp_file,
    'get_tmp_file': get_tmp_file,
    'clean_tmp_file': clean_tmp_file
}
