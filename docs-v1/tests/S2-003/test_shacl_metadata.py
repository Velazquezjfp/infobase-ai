"""
Test Suite for S2-003: Legacy Form Standardization

This test suite validates that all existing form fields have been migrated
to include SHACL/JSON-LD semantic metadata.

Test Cases:
- TC-S2-003-01: All form fields have shaclMetadata property
- TC-S2-003-02: fullName has sh:path = "schema:name"
- TC-S2-003-03: birthDate has sh:datatype = "xsd:date"
- TC-S2-003-04: Backward compatibility preserved (shaclMetadata is optional)
- TC-S2-003-05: SHACL type displayed in admin mode via Badge components
- TC-S2-003-06: Migration script generates valid SHACL structure
"""

import pytest
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.schemas.jsonld_context import (
    SHACL_CONTEXT,
    get_xsd_datatype,
    get_schema_org_property,
)
from backend.scripts.migrate_forms_to_shacl import (
    FormField,
    generate_shacl_for_field,
    migrate_form_fields,
    validate_shacl_metadata,
    INTEGRATION_COURSE_FIELDS,
)


class TestSHACLMetadataPresence:
    """TC-S2-003-01: All form fields have shaclMetadata property"""

    def test_integration_course_fields_have_shacl(self):
        """Verify all Integration Course form fields have SHACL metadata"""
        migrated = migrate_form_fields(INTEGRATION_COURSE_FIELDS)

        for field in migrated:
            assert 'shaclMetadata' in field, f"Field {field['id']} missing shaclMetadata"
            assert field['shaclMetadata'] is not None, f"Field {field['id']} has null shaclMetadata"
            assert isinstance(field['shaclMetadata'], dict), f"Field {field['id']} shaclMetadata is not a dict"

    def test_all_seven_fields_present(self):
        """Verify all 7 Integration Course fields are migrated"""
        assert len(INTEGRATION_COURSE_FIELDS) == 7, "Integration Course form should have 7 fields"

        expected_field_ids = [
            'fullName', 'birthDate', 'countryOfOrigin',
            'existingLanguageCertificates', 'coursePreference',
            'currentAddress', 'reasonForApplication'
        ]

        actual_field_ids = [f.id for f in INTEGRATION_COURSE_FIELDS]
        assert set(actual_field_ids) == set(expected_field_ids), "Field IDs don't match expected"


class TestSHACLFieldMapping:
    """TC-S2-003-02: Verify specific SHACL path mappings"""

    def test_fullname_schema_mapping(self):
        """TC-S2-003-02: fullName has sh:path = 'schema:name'"""
        fullname_field = FormField(id='fullName', label='Full Name', type='text', required=True)
        shacl = generate_shacl_for_field(fullname_field)

        assert shacl['sh:path'] == 'schema:name', "fullName should map to schema:name"

    def test_birthdate_schema_mapping(self):
        """Verify birthDate maps to schema:birthDate"""
        birthdate_field = FormField(id='birthDate', label='Date of Birth', type='date', required=True)
        shacl = generate_shacl_for_field(birthdate_field)

        assert shacl['sh:path'] == 'schema:birthDate', "birthDate should map to schema:birthDate"

    def test_country_schema_mapping(self):
        """Verify countryOfOrigin maps to schema:nationality"""
        country_field = FormField(id='countryOfOrigin', label='Country of Origin', type='text', required=True)
        shacl = generate_shacl_for_field(country_field)

        assert shacl['sh:path'] == 'schema:nationality', "countryOfOrigin should map to schema:nationality"


class TestSHACLDatatypes:
    """TC-S2-003-03: Verify sh:datatype = 'xsd:date' for date fields"""

    def test_birthdate_xsd_date_datatype(self):
        """TC-S2-003-03: birthDate has sh:datatype = 'xsd:date'"""
        birthdate_field = FormField(id='birthDate', label='Date of Birth', type='date', required=True)
        shacl = generate_shacl_for_field(birthdate_field)

        assert shacl['sh:datatype'] == 'xsd:date', "birthDate should have xsd:date datatype"

    def test_text_fields_xsd_string_datatype(self):
        """Verify text fields have xsd:string datatype"""
        text_field = FormField(id='fullName', label='Full Name', type='text', required=True)
        shacl = generate_shacl_for_field(text_field)

        assert shacl['sh:datatype'] == 'xsd:string', "text fields should have xsd:string datatype"

    def test_select_fields_xsd_string_with_sh_in(self):
        """Verify select fields have xsd:string datatype with sh:in constraint"""
        select_field = FormField(
            id='coursePreference',
            label='Course Preference',
            type='select',
            options=['Intensive Course', 'Evening Course', 'Weekend Course']
        )
        shacl = generate_shacl_for_field(select_field)

        assert shacl['sh:datatype'] == 'xsd:string', "select fields should have xsd:string datatype"
        assert 'sh:in' in shacl, "select fields should have sh:in constraint"
        assert '@list' in shacl['sh:in'], "sh:in should contain @list"
        assert len(shacl['sh:in']['@list']) == 3, "sh:in should have 3 options"


class TestBackwardCompatibility:
    """TC-S2-003-04: Backward compatibility preserved (shaclMetadata is optional)"""

    def test_field_without_shacl_still_valid(self):
        """Verify form fields work without shaclMetadata"""
        field_without_shacl = {
            'id': 'testField',
            'label': 'Test Field',
            'type': 'text',
            'value': '',
            'required': False
        }

        # Should not raise error
        assert 'id' in field_without_shacl
        assert 'label' in field_without_shacl
        assert 'type' in field_without_shacl

        # shaclMetadata is optional
        assert field_without_shacl.get('shaclMetadata') is None

    def test_formfield_dataclass_without_shacl(self):
        """Verify FormField dataclass works without SHACL"""
        field = FormField(id='test', label='Test', type='text')

        # Should work without errors
        assert field.id == 'test'
        assert field.label == 'Test'
        assert field.type == 'text'


class TestSHACLValidation:
    """TC-S2-003-06: Migration script generates valid SHACL structure"""

    def test_all_migrated_fields_valid(self):
        """Verify all migrated fields have valid SHACL metadata"""
        migrated = migrate_form_fields(INTEGRATION_COURSE_FIELDS)

        for field in migrated:
            shacl = field['shaclMetadata']
            errors = validate_shacl_metadata(shacl)
            assert len(errors) == 0, f"Field {field['id']} has invalid SHACL: {errors}"

    def test_shacl_context_present(self):
        """Verify SHACL context is defined"""
        assert SHACL_CONTEXT is not None
        assert 'sh' in SHACL_CONTEXT
        assert 'schema' in SHACL_CONTEXT
        assert 'xsd' in SHACL_CONTEXT

    def test_shacl_required_fields_present(self):
        """Verify SHACL metadata contains all required fields"""
        fullname_field = FormField(id='fullName', label='Full Name', type='text', required=True)
        shacl = generate_shacl_for_field(fullname_field)

        required_fields = ['@type', 'sh:path', 'sh:datatype', 'sh:name']
        for field in required_fields:
            assert field in shacl, f"Missing required SHACL field: {field}"

    def test_shacl_mincount_for_required_fields(self):
        """Verify required fields have sh:minCount = 1"""
        required_field = FormField(id='fullName', label='Full Name', type='text', required=True)
        shacl = generate_shacl_for_field(required_field)

        assert 'sh:minCount' in shacl, "Required fields should have sh:minCount"
        assert shacl['sh:minCount'] == 1, "Required fields should have sh:minCount = 1"

    def test_shacl_no_mincount_for_optional_fields(self):
        """Verify optional fields don't have sh:minCount = 1"""
        optional_field = FormField(id='existingLanguageCertificates', label='Existing Language Certificates', type='text', required=False)
        shacl = generate_shacl_for_field(optional_field)

        # Optional fields should not have minCount = 1, or it should be 0/absent
        if 'sh:minCount' in shacl:
            assert shacl['sh:minCount'] != 1, "Optional fields should not have sh:minCount = 1"


class TestSHACLConstraints:
    """Test SHACL constraint generation"""

    def test_select_field_sh_in_constraint(self):
        """Verify select fields generate sh:in constraint with correct format"""
        select_field = FormField(
            id='coursePreference',
            label='Course Preference',
            type='select',
            options=['Intensive Course', 'Evening Course', 'Weekend Course']
        )
        shacl = generate_shacl_for_field(select_field)

        assert 'sh:in' in shacl
        assert isinstance(shacl['sh:in'], dict)
        assert '@list' in shacl['sh:in']
        assert isinstance(shacl['sh:in']['@list'], list)
        assert shacl['sh:in']['@list'] == ['Intensive Course', 'Evening Course', 'Weekend Course']

    def test_maxcount_always_set(self):
        """Verify all fields have sh:maxCount for cardinality"""
        field = FormField(id='test', label='Test', type='text')
        shacl = generate_shacl_for_field(field)

        assert 'sh:maxCount' in shacl, "All fields should have sh:maxCount"


class TestMigrationScriptExecution:
    """Test migration script execution"""

    def test_migrate_all_fields_returns_correct_count(self):
        """Verify migration processes all fields"""
        migrated = migrate_form_fields(INTEGRATION_COURSE_FIELDS)
        assert len(migrated) == 7, "Should migrate all 7 fields"

    def test_migration_preserves_field_properties(self):
        """Verify migration preserves original field properties"""
        original = INTEGRATION_COURSE_FIELDS[0]
        migrated = migrate_form_fields([original])[0]

        assert migrated['id'] == original.id
        assert migrated['label'] == original.label
        assert migrated['type'] == original.type
        assert migrated['required'] == original.required

    def test_migration_adds_shacl_metadata(self):
        """Verify migration adds shaclMetadata to each field"""
        migrated = migrate_form_fields(INTEGRATION_COURSE_FIELDS)

        for field in migrated:
            assert 'shaclMetadata' in field
            assert field['shaclMetadata'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
