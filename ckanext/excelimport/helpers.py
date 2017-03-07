from ckan.logic import ValidationError

import cgi

import ckanext.scheming.helpers as schema_helpers
from ckanext.excelimport import FIELD_MAPPING

schema = schema_helpers.scheming_get_schema('dataset', 'dataset')


def validate_file_ext(zip_file):
    """Validate for .zip file passed into the form."""
    if not zip_file.lower().endswith('.zip'):
        raise ValidationError({'message': 'Please, upload a zip archive'})


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
                    mt_field = schema_helpers.scheming_field_by_name(
                        schema.get('dataset_fields', {}),
                        FIELD_MAPPING[field]
                    )
                    choices = schema_helpers.scheming_field_choices(
                        mt_field
                    )

                    for choice in choices:
                        if choice.get('label') == value:
                            value = choice.get('value', None)

                data_dict[FIELD_MAPPING[field]] = value
        except KeyError, e:
            raise e


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
    'prepare_data_dict': prepare_data_dict,
    'prepare_file': prepare_file
}
