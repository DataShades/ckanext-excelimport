AVAILABLE_MD_FILES = ['spatial-dataset.xlsx', 'dataset.xlsx']
METADATA_SHEET = {
    'dataset.xlsx': 'Non-Spatial Metadata',
    'spatial-dataset.xlsx': 'Spatial Metadata'
}

FIELD_MAPPING = {
    'CKAN Package ID': 'id',
    'Title': 'title',
    'File Identifier': 'file_identifier',
    'Abstract': 'notes',
    'Purpose': 'purpose',
    'Contact': 'custodian',
    'Jurisdictions': 'jurisdictions',
    'Geographic Bounding Box': 'geographic_bounding_box',
    'Geographic Area': 'geographic_area',
    'Lineage': 'lineage',
    'Extent': 'spatial',
    'Distribution Format': 'distribution_format',
    'Keyword': 'tag_string',
    'Maintenance And Update Frequency': 'update_frequency',
    'Use Limitation': 'use_limitation',
    'Legal Constraints': 'legal_constraints',
    'Resolution': 'resolution',
    'DQ Completeness': 'dq_completeness',
    'Reference System': 'reference_system',
    'Topic Category': 'topic',
    'Date Created': 'created_bug',
    'Date Published': 'not_used',
    'Date Last Revised': 'last_modified_fix',
}
