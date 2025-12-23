"""
SHACL (Shapes Constraint Language) Schema Definitions

This module provides Python dataclasses for representing SHACL shapes
in JSON-LD format. SHACL is used to define and validate the structure
of form fields with semantic meaning.

References:
- SHACL Spec: https://www.w3.org/TR/shacl/
- JSON-LD: https://json-ld.org/
- Schema.org: https://schema.org/
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class SHACLPropertyShape:
    """
    Represents a SHACL PropertyShape for a single form field.

    A PropertyShape defines constraints on a property of a node,
    including its datatype, cardinality, and allowed values.

    Attributes:
        sh_path: The property path (e.g., "schema:name", "schema:birthDate")
        sh_datatype: XSD datatype (e.g., "xsd:string", "xsd:date")
        sh_name: Human-readable name for the property
        sh_description: Optional description of the property
        sh_min_count: Minimum cardinality (1 = required)
        sh_max_count: Maximum cardinality (1 = single value)
        sh_in: List of allowed values (for select/enum fields)
        sh_pattern: Optional regex pattern for validation
        sh_min_length: Minimum string length
        sh_max_length: Maximum string length
    """
    sh_path: str
    sh_datatype: str
    sh_name: str
    sh_description: Optional[str] = None
    sh_min_count: Optional[int] = None
    sh_max_count: Optional[int] = None
    sh_in: Optional[List[str]] = None
    sh_pattern: Optional[str] = None
    sh_min_length: Optional[int] = None
    sh_max_length: Optional[int] = None

    def to_jsonld(self, include_context: bool = True) -> Dict[str, Any]:
        """
        Convert the PropertyShape to a JSON-LD dictionary.

        Args:
            include_context: Whether to include the @context in output

        Returns:
            JSON-LD representation of the PropertyShape
        """
        result: Dict[str, Any] = {
            "@type": "sh:PropertyShape",
            "sh:path": self.sh_path,
            "sh:datatype": self.sh_datatype,
            "sh:name": self.sh_name,
        }

        if include_context:
            result["@context"] = {
                "sh": "http://www.w3.org/ns/shacl#",
                "schema": "http://schema.org/",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            }

        if self.sh_description is not None:
            result["sh:description"] = self.sh_description

        if self.sh_min_count is not None:
            result["sh:minCount"] = self.sh_min_count

        if self.sh_max_count is not None:
            result["sh:maxCount"] = self.sh_max_count

        if self.sh_in is not None:
            result["sh:in"] = {"@list": self.sh_in}

        if self.sh_pattern is not None:
            result["sh:pattern"] = self.sh_pattern

        if self.sh_min_length is not None:
            result["sh:minLength"] = self.sh_min_length

        if self.sh_max_length is not None:
            result["sh:maxLength"] = self.sh_max_length

        return result

    @classmethod
    def from_jsonld(cls, data: Dict[str, Any]) -> "SHACLPropertyShape":
        """
        Create a SHACLPropertyShape from a JSON-LD dictionary.

        Args:
            data: JSON-LD dictionary representation

        Returns:
            SHACLPropertyShape instance
        """
        sh_in = None
        if "sh:in" in data:
            sh_in_value = data["sh:in"]
            if isinstance(sh_in_value, dict) and "@list" in sh_in_value:
                sh_in = sh_in_value["@list"]
            elif isinstance(sh_in_value, list):
                sh_in = sh_in_value

        return cls(
            sh_path=data.get("sh:path", ""),
            sh_datatype=data.get("sh:datatype", "xsd:string"),
            sh_name=data.get("sh:name", ""),
            sh_description=data.get("sh:description"),
            sh_min_count=data.get("sh:minCount"),
            sh_max_count=data.get("sh:maxCount"),
            sh_in=sh_in,
            sh_pattern=data.get("sh:pattern"),
            sh_min_length=data.get("sh:minLength"),
            sh_max_length=data.get("sh:maxLength"),
        )


@dataclass
class SHACLNodeShape:
    """
    Represents a SHACL NodeShape for a form or entity.

    A NodeShape defines constraints on a node (e.g., a form or entity),
    including which properties it should have and their constraints.

    Attributes:
        sh_target_class: The target class (e.g., "schema:Person")
        sh_name: Human-readable name for the shape
        sh_description: Optional description of the shape
        sh_properties: List of PropertyShapes for this node
    """
    sh_target_class: str
    sh_name: str
    sh_description: Optional[str] = None
    sh_properties: List[SHACLPropertyShape] = field(default_factory=list)

    def to_jsonld(self) -> Dict[str, Any]:
        """
        Convert the NodeShape to a JSON-LD dictionary.

        Returns:
            JSON-LD representation of the NodeShape
        """
        return {
            "@context": {
                "sh": "http://www.w3.org/ns/shacl#",
                "schema": "http://schema.org/",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            },
            "@type": "sh:NodeShape",
            "sh:targetClass": self.sh_target_class,
            "sh:name": self.sh_name,
            "sh:description": self.sh_description,
            "sh:property": [
                prop.to_jsonld(include_context=False)
                for prop in self.sh_properties
            ]
        }

    @classmethod
    def from_jsonld(cls, data: Dict[str, Any]) -> "SHACLNodeShape":
        """
        Create a SHACLNodeShape from a JSON-LD dictionary.

        Args:
            data: JSON-LD dictionary representation

        Returns:
            SHACLNodeShape instance
        """
        properties = []
        if "sh:property" in data:
            for prop_data in data["sh:property"]:
                properties.append(SHACLPropertyShape.from_jsonld(prop_data))

        return cls(
            sh_target_class=data.get("sh:targetClass", ""),
            sh_name=data.get("sh:name", ""),
            sh_description=data.get("sh:description"),
            sh_properties=properties,
        )

    def add_property(self, prop: SHACLPropertyShape) -> None:
        """
        Add a PropertyShape to this NodeShape.

        Args:
            prop: The PropertyShape to add
        """
        self.sh_properties.append(prop)

    def get_property(self, path: str) -> Optional[SHACLPropertyShape]:
        """
        Get a PropertyShape by its path.

        Args:
            path: The property path to search for

        Returns:
            The PropertyShape if found, None otherwise
        """
        for prop in self.sh_properties:
            if prop.sh_path == path:
                return prop
        return None
