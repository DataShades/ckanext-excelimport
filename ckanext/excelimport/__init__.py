AVAILABLE_MD_FILES = ['dataset.xlsx']
METADATA_SHEET = {
    'dataset.xlsx': 'Dataset Metadata',
}

FIELD_MAPPING = {
    'CKAN Package ID': 'id',
    'Title': 'title',
    'File Identifier': 'file_identifier',
    'Description': 'notes',
    'Tags': 'tag_string',
    'Custodian': 'custodian',
    'Author Email': 'author_email',
    'License': 'license',
    'Organisation ID': 'owner_org',
    'Visibility': 'private',
    'Landing Page': 'url',
    'Extent': 'spatial',
    'Temporal Coverage': 'temporal_extent',
    'Frequency of change': 'update_frequency',
    'Type': 'type',
    'Topic and category': 'topic',
    'Date Created': 'created',
    'Last updated': 'last_modified',
    'Map Service ID': 'map_service_id',
    'Layer ID': 'layer_id',
    'Map Type': 'map_type'
}

MAP_TYPES = {
    'Map Service and Layer': 'MapServiceLayer',
    'WMS Layer': 'Layer',
    'Map Service': 'MapService'
}
