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

# XML mapping
NAMESPACES = {
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gml': 'http://www.opengis.net/gml'
}

XML_MAP = {
    'title': (
        'gmd:identificationInfo/gmd:MD_DataIdentification/'
        'gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString'),
    'notes': (
        'gmd:identificationInfo/gmd:MD_DataIdentification/'
        'gmd:abstract/gco:CharacterString'),
    'tag_string': {
        'x_value': (
            'gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:descriptiveKeywords/gmd:MD_Keywords'),
        'x_iter': 'gmd:keyword/gco:CharacterString'
    },
    'custodian': (
        'gmd:contact/gmd:CI_ResponsibleParty/'
        'gmd:organisationName/gco:CharacterString'),
    'author_email': (
        'gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/'
        'gmd:CI_Contact/gmd:address/gmd:CI_Address/'
        'gmd:electronicMailAddress/gco:CharacterString'),
    'license': '',
    'owner_org': (
        'gmd:contact/gmd:CI_ResponsibleParty/'
        'gmd:organisationName/gco:CharacterString'),
    'private': '',
    'url': '',
    'spatial': {
        'x_value': (
            'gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent'),
        'x_coords': {
            'west': (
                'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
                'gmd:westBoundLongitude/gco:Decimal'),
            'east': (
                'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
                'gmd:eastBoundLongitude/gco:Decimal'),
            'south': (
                'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
                'gmd:southBoundLatitude/gco:Decimal'),
            'north': (
                'gmd:geographicElement/gmd:EX_GeographicBoundingBox/'
                'gmd:northBoundLatitude/gco:Decimal')
        }
    },
    'temporal_extent': {
        'x_value': (
            'gmd:identificationInfo/gmd:MD_DataIdentification/'
            'gmd:extent/gmd:EX_Extent'),
        'x_temporal': {
            'begin': (
                'gmd:temporalElement[2]/gmd:EX_TemporalExtent/'
                'gmd:extent/gml:TimePeriod/gml:beginPosition'),
            'end': (
                'gmd:temporalElement[2]/gmd:EX_TemporalExtent/'
                'gmd:extent/gml:TimePeriod/gml:endPosition')
        }
    },
    'topic': (
        'gmd:identificationInfo/gmd:MD_DataIdentification/'
        'gmd:topicCategory[1]/gmd:MD_TopicCategoryCode'),
    'update_frequency': (
        'gmd:identificationInfo/gmd:MD_DataIdentification/'
        'gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/'
        'gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode'),
    'type': '',
    'created': (
        'gmd:identificationInfo/gmd:MD_DataIdentification/'
        'gmd:citation/gmd:CI_Citation/gmd:date[1]/'
        'gmd:CI_Date/gmd:date/gco:Date'),
    'last_modified': (
        'gmd:identificationInfo/gmd:MD_DataIdentification/'
        'gmd:citation/gmd:CI_Citation/gmd:date[3]/'
        'gmd:CI_Date/gmd:date/gco:Date')
}
