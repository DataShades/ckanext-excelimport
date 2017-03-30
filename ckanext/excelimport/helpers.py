from ckan.logic import ValidationError

import shapely.geometry as geo
import cgi
from dateutil.parser import parse

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
            for tag in tag_list.iterfind(value['x_iter'], NAMESPACES):
                tags.append(tag.text)
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
        elif key == 'update_frequency':
            frequency = tree.find(value, NAMESPACES)
            if frequency.text:
                data_dict[key] = frequency.text
            else:
                data_dict[key] = 'Unknown'
        elif key == 'type':
            data_dict[key] = 'dataset'
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


get_helpers = {
    'validate_file_ext': validate_file_ext,
    'validate_file_xml': validate_file_xml,
    'prepare_data_dict': prepare_data_dict,
    'prepare_dict_from_xml': prepare_dict_from_xml,
    'prepare_file': prepare_file
}
