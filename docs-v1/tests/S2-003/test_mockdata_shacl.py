"""
Test Suite for S2-003: MockData SHACL Metadata Validation

This test suite validates that mockData.ts has been properly updated
with SHACL metadata for all form templates.

Test Cases:
- Verify integrationCourseFormTemplate has SHACL metadata
- Verify asylumApplicationFormTemplate has SHACL metadata
- Verify familyReunificationFormTemplate has SHACL metadata
- Verify all fields have correct SHACL path mappings
- Verify all date fields have xsd:date datatype
"""

import pytest
import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestMockDataSHACLMetadata:
    """Validate mockData.ts contains SHACL metadata"""

    @pytest.fixture
    def mockdata_content(self):
        """Load mockData.ts file content"""
        mockdata_path = project_root / 'src' / 'data' / 'mockData.ts'
        with open(mockdata_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_mockdata_file_exists(self, mockdata_content):
        """Verify mockData.ts exists and is readable"""
        assert mockdata_content is not None
        assert len(mockdata_content) > 0

    def test_shacl_context_imported(self, mockdata_content):
        """Verify SHACL_CONTEXT is imported"""
        assert 'SHACL_CONTEXT' in mockdata_content
        assert "from '@/types/shacl'" in mockdata_content

    def test_integration_course_template_has_shacl(self, mockdata_content):
        """Verify integrationCourseFormTemplate includes shaclMetadata"""
        # Check that integrationCourseFormTemplate is defined
        assert 'integrationCourseFormTemplate' in mockdata_content

        # Check for shaclMetadata in the template section
        template_start = mockdata_content.find('integrationCourseFormTemplate')
        template_end = mockdata_content.find('];', template_start)
        template_section = mockdata_content[template_start:template_end]

        # Count shaclMetadata occurrences (should be 7, one per field)
        shacl_count = template_section.count('shaclMetadata:')
        assert shacl_count == 7, f"Expected 7 shaclMetadata entries, found {shacl_count}"

    def test_asylum_application_template_has_shacl(self, mockdata_content):
        """Verify asylumApplicationFormTemplate includes shaclMetadata"""
        assert 'asylumApplicationFormTemplate' in mockdata_content

        template_start = mockdata_content.find('asylumApplicationFormTemplate')
        template_end = mockdata_content.find('];', template_start)
        template_section = mockdata_content[template_start:template_end]

        # Count shaclMetadata occurrences (should be 7 fields)
        shacl_count = template_section.count('shaclMetadata:')
        assert shacl_count == 7, f"Expected 7 shaclMetadata entries, found {shacl_count}"

    def test_family_reunification_template_has_shacl(self, mockdata_content):
        """Verify familyReunificationFormTemplate includes shaclMetadata"""
        assert 'familyReunificationFormTemplate' in mockdata_content

        template_start = mockdata_content.find('familyReunificationFormTemplate')
        template_end = mockdata_content.find('];', template_start)
        template_section = mockdata_content[template_start:template_end]

        # Count shaclMetadata occurrences (should be 7 fields)
        shacl_count = template_section.count('shaclMetadata:')
        assert shacl_count == 7, f"Expected 7 shaclMetadata entries, found {shacl_count}"

    def test_fullname_schema_name_mapping(self, mockdata_content):
        """Verify fullName fields map to schema:name"""
        # Find all fullName field definitions
        fullname_pattern = r"id:\s*'fullName'.*?'sh:path':\s*'(schema:\w+)'"
        matches = re.findall(fullname_pattern, mockdata_content, re.DOTALL)

        # All fullName fields should map to schema:name
        assert len(matches) >= 3, "Should find fullName in at least 3 templates"
        for match in matches:
            assert match == 'schema:name', f"fullName should map to schema:name, found {match}"

    def test_birthdate_xsd_date_datatype(self, mockdata_content):
        """Verify birthDate fields have xsd:date datatype"""
        # Find all birthDate field definitions
        birthdate_pattern = r"id:\s*'birthDate'.*?'sh:datatype':\s*'(xsd:\w+)'"
        matches = re.findall(birthdate_pattern, mockdata_content, re.DOTALL)

        # All birthDate fields should have xsd:date
        assert len(matches) >= 3, "Should find birthDate in at least 3 templates"
        for match in matches:
            assert match == 'xsd:date', f"birthDate should have xsd:date datatype, found {match}"

    def test_country_origin_nationality_mapping(self, mockdata_content):
        """Verify countryOfOrigin maps to schema:nationality"""
        country_pattern = r"id:\s*'countryOfOrigin'.*?'sh:path':\s*'(schema:\w+)'"
        matches = re.findall(country_pattern, mockdata_content, re.DOTALL)

        assert len(matches) >= 3, "Should find countryOfOrigin in at least 3 templates"
        for match in matches:
            assert match == 'schema:nationality', f"countryOfOrigin should map to schema:nationality, found {match}"

    def test_course_preference_sh_in_constraint(self, mockdata_content):
        """Verify coursePreference has sh:in constraint"""
        # Find coursePreference field
        course_start = mockdata_content.find("id: 'coursePreference'")
        if course_start != -1:
            course_section_end = mockdata_content.find('},\n  {', course_start)
            course_section = mockdata_content[course_start:course_section_end]

            assert "'sh:in':" in course_section, "coursePreference should have sh:in constraint"
            assert "'@list':" in course_section, "sh:in should have @list"
            assert 'Intensive Course' in course_section, "sh:in should contain 'Intensive Course'"

    def test_address_field_mapping(self, mockdata_content):
        """Verify currentAddress maps to schema:address"""
        address_pattern = r"id:\s*'currentAddress'.*?'sh:path':\s*'(schema:\w+)'"
        matches = re.findall(address_pattern, mockdata_content, re.DOTALL)

        assert len(matches) >= 3, "Should find currentAddress in at least 3 templates"
        for match in matches:
            assert match == 'schema:address', f"currentAddress should map to schema:address, found {match}"

    def test_shacl_context_used(self, mockdata_content):
        """Verify SHACL_CONTEXT is used in shaclMetadata"""
        # Check that '@context': SHACL_CONTEXT pattern exists
        assert "'@context': SHACL_CONTEXT" in mockdata_content, "SHACL_CONTEXT should be used in @context"

    def test_all_fields_have_sh_type(self, mockdata_content):
        """Verify all shaclMetadata have @type: sh:PropertyShape"""
        shacl_count = mockdata_content.count('shaclMetadata:')
        type_count = mockdata_content.count("'@type': 'sh:PropertyShape'")

        # Should have equal counts
        assert shacl_count == type_count, f"All {shacl_count} shaclMetadata should have @type, found {type_count}"

    def test_required_fields_have_mincount(self, mockdata_content):
        """Verify required fields have sh:minCount: 1"""
        # Find fullName field (required: true)
        fullname_start = mockdata_content.find("id: 'fullName'")
        fullname_end = mockdata_content.find('},\n  {', fullname_start)
        fullname_section = mockdata_content[fullname_start:fullname_end]

        assert 'required: true' in fullname_section
        assert "'sh:minCount': 1" in fullname_section, "Required fields should have sh:minCount: 1"


class TestFormTemplateStructure:
    """Validate form template structure"""

    @pytest.fixture
    def mockdata_content(self):
        """Load mockData.ts file content"""
        mockdata_path = project_root / 'src' / 'data' / 'mockData.ts'
        with open(mockdata_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_three_form_templates_defined(self, mockdata_content):
        """Verify all three form templates are defined"""
        assert 'integrationCourseFormTemplate' in mockdata_content
        assert 'asylumApplicationFormTemplate' in mockdata_content
        assert 'familyReunificationFormTemplate' in mockdata_content

    def test_case_form_templates_mapping(self, mockdata_content):
        """Verify caseFormTemplates mapping exists"""
        assert 'caseFormTemplates' in mockdata_content
        assert "'integration_course': integrationCourseFormTemplate" in mockdata_content
        assert "'asylum_application': asylumApplicationFormTemplate" in mockdata_content
        assert "'family_reunification': familyReunificationFormTemplate" in mockdata_content

    def test_initial_form_fields_uses_integration_template(self, mockdata_content):
        """Verify initialFormFields uses integrationCourseFormTemplate"""
        assert 'initialFormFields' in mockdata_content
        assert 'initialFormFields: FormField[] = integrationCourseFormTemplate' in mockdata_content


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
