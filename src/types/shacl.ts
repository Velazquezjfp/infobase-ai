/**
 * SHACL (Shapes Constraint Language) TypeScript Interfaces
 *
 * These interfaces mirror the Python dataclasses in backend/models/shacl_property_shape.py
 * and backend/schemas/validation_patterns.py.
 * They represent SHACL shapes in JSON-LD format for form field metadata and validation.
 *
 * References:
 * - SHACL Spec: https://www.w3.org/TR/shacl/
 * - JSON-LD: https://json-ld.org/
 * - Schema.org: https://schema.org/
 */

/**
 * Validation pattern with regex and error message.
 * Mirrors backend/schemas/validation_patterns.py::ValidationPattern
 */
export interface ValidationPattern {
  /** Regular expression for validation */
  pattern: string;
  /** User-friendly error message displayed on validation failure */
  message: string;
}

/**
 * JSON-LD Context type for namespace definitions
 */
export interface JSONLDContext {
  sh: string;
  schema: string;
  xsd: string;
  rdf?: string;
  rdfs?: string;
  [key: string]: string | undefined;
}

/**
 * Standard SHACL context with common namespaces
 */
export const SHACL_CONTEXT: JSONLDContext = {
  sh: "http://www.w3.org/ns/shacl#",
  schema: "http://schema.org/",
  xsd: "http://www.w3.org/2001/XMLSchema#",
  rdf: "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  rdfs: "http://www.w3.org/2000/01/rdf-schema#",
};

/**
 * Mapping from form field types to XSD datatypes
 */
export const XSD_DATATYPE_MAPPING: Record<string, string> = {
  text: "xsd:string",
  date: "xsd:date",
  select: "xsd:string",
  textarea: "xsd:string",
  number: "xsd:integer",
  email: "xsd:string",
  phone: "xsd:string",
  boolean: "xsd:boolean",
};

/**
 * Validation patterns for common field types.
 * Mirrors backend/schemas/validation_patterns.py
 */

/** Email validation pattern */
export const EMAIL_PATTERN: ValidationPattern = {
  pattern: "^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$",
  message: "Email must be a valid email address containing @ and a domain"
};

/** Phone number validation pattern */
export const PHONE_PATTERN: ValidationPattern = {
  pattern: "^[\\+]?[(]?[0-9]{1,4}[)]?[-\\s\\.]?[(]?[0-9]{1,4}[)]?[-\\s\\.]?[0-9]{1,9}$",
  message: "Phone number must be valid (e.g., +49 123 456789 or 123-456-7890)"
};

/** Name validation pattern */
export const NAME_PATTERN: ValidationPattern = {
  pattern: "^[\\p{L}\\s\\-']{2,}$",
  message: "Name must contain at least 2 characters and only letters, spaces, hyphens, or apostrophes"
};

/** Date validation pattern (ISO 8601: YYYY-MM-DD) */
export const DATE_PATTERN: ValidationPattern = {
  pattern: "^\\d{4}-\\d{2}-\\d{2}$",
  message: "Date must be in YYYY-MM-DD format"
};

/** Address validation pattern */
export const ADDRESS_PATTERN: ValidationPattern = {
  pattern: "^[\\p{L}\\p{N}\\s,.\\-]{5,}$",
  message: "Address must contain at least 5 characters"
};

/**
 * Registry of validation patterns by field type
 */
export const VALIDATION_PATTERNS: Record<string, ValidationPattern> = {
  email: EMAIL_PATTERN,
  phone: PHONE_PATTERN,
  telephone: PHONE_PATTERN,
  name: NAME_PATTERN,
  givenName: NAME_PATTERN,
  familyName: NAME_PATTERN,
  date: DATE_PATTERN,
  birthDate: DATE_PATTERN,
  address: ADDRESS_PATTERN,
};

/**
 * JSON-LD list structure for sh:in values
 */
export interface SHACLList {
  "@list": string[];
}

/**
 * SHACL PropertyShape interface
 *
 * Represents constraints on a single form field property.
 * This interface mirrors the Python SHACLPropertyShape dataclass.
 */
export interface SHACLPropertyShape {
  /** JSON-LD context (optional when nested in NodeShape) */
  "@context"?: JSONLDContext;

  /** RDF type - always "sh:PropertyShape" */
  "@type": "sh:PropertyShape";

  /** Property path (e.g., "schema:name", "schema:birthDate") */
  "sh:path": string;

  /** XSD datatype (e.g., "xsd:string", "xsd:date") */
  "sh:datatype": string;

  /** Human-readable name */
  "sh:name": string;

  /** User-friendly validation error message */
  "sh:message": string;

  /** Optional description */
  "sh:description"?: string;

  /** Minimum cardinality (1 = required) */
  "sh:minCount"?: number;

  /** Maximum cardinality (1 = single value) */
  "sh:maxCount"?: number;

  /** Allowed values for select/enum fields */
  "sh:in"?: SHACLList;

  /** Regex pattern for validation */
  "sh:pattern"?: string;

  /** Minimum string length */
  "sh:minLength"?: number;

  /** Maximum string length */
  "sh:maxLength"?: number;
}

/**
 * SHACL NodeShape interface
 *
 * Represents constraints on a form or entity (collection of properties).
 * This interface mirrors the Python SHACLNodeShape dataclass.
 */
export interface SHACLNodeShape {
  /** JSON-LD context */
  "@context": JSONLDContext;

  /** RDF type - always "sh:NodeShape" */
  "@type": "sh:NodeShape";

  /** Target class (e.g., "schema:Person", "schema:Thing") */
  "sh:targetClass": string;

  /** Human-readable name */
  "sh:name": string;

  /** Optional description */
  "sh:description"?: string;

  /** List of property shapes */
  "sh:property": SHACLPropertyShape[];
}

/**
 * Helper function to create a SHACLPropertyShape
 */
export function createPropertyShape(
  path: string,
  name: string,
  datatype: string = "xsd:string",
  options?: {
    description?: string;
    message?: string;
    required?: boolean;
    allowedValues?: string[];
    pattern?: string;
    minLength?: number;
    maxLength?: number;
  }
): SHACLPropertyShape {
  // Determine validation message
  let message = options?.message;

  // If no message provided, try to get pattern from registry
  if (!message) {
    const propertyName = path.includes(":") ? path.split(":")[1] : path;
    const validationPattern = VALIDATION_PATTERNS[propertyName.toLowerCase()];

    if (validationPattern) {
      message = validationPattern.message;
      // Use pattern from registry if not explicitly provided
      if (!options?.pattern) {
        options = { ...options, pattern: validationPattern.pattern };
      }
    } else {
      // Default message
      message = options?.required
        ? `${name} is required`
        : `${name} is invalid`;
    }
  }

  const shape: SHACLPropertyShape = {
    "@context": SHACL_CONTEXT,
    "@type": "sh:PropertyShape",
    "sh:path": path,
    "sh:datatype": datatype,
    "sh:name": name,
    "sh:message": message,
    "sh:maxCount": 1,
  };

  if (options?.description) {
    shape["sh:description"] = options.description;
  }

  if (options?.required) {
    shape["sh:minCount"] = 1;
  }

  if (options?.allowedValues && options.allowedValues.length > 0) {
    shape["sh:in"] = { "@list": options.allowedValues };
  }

  if (options?.pattern) {
    shape["sh:pattern"] = options.pattern;
  }

  if (options?.minLength !== undefined) {
    shape["sh:minLength"] = options.minLength;
  }

  if (options?.maxLength !== undefined) {
    shape["sh:maxLength"] = options.maxLength;
  }

  return shape;
}

/**
 * Helper function to create a SHACLNodeShape
 */
export function createNodeShape(
  name: string,
  targetClass: string = "schema:Thing",
  description?: string
): SHACLNodeShape {
  return {
    "@context": SHACL_CONTEXT,
    "@type": "sh:NodeShape",
    "sh:targetClass": targetClass,
    "sh:name": name,
    "sh:description": description,
    "sh:property": [],
  };
}

/**
 * Get XSD datatype for a form field type
 */
export function getXsdDatatype(fieldType: string): string {
  return XSD_DATATYPE_MAPPING[fieldType.toLowerCase()] || "xsd:string";
}

/**
 * Check if a property shape indicates a required field
 */
export function isRequired(shape: SHACLPropertyShape): boolean {
  return (shape["sh:minCount"] ?? 0) >= 1;
}

/**
 * Get allowed values from a property shape (for select fields)
 */
export function getAllowedValues(shape: SHACLPropertyShape): string[] | undefined {
  return shape["sh:in"]?.["@list"];
}

/**
 * Get validation pattern by field type
 */
export function getValidationPattern(fieldType: string): ValidationPattern | undefined {
  return VALIDATION_PATTERNS[fieldType.toLowerCase()];
}

/**
 * Get validation pattern for a schema.org property
 */
export function getPatternForSchemaOrgProperty(schemaProperty: string): ValidationPattern | undefined {
  // Extract property name from schema.org path (e.g., "schema:email" -> "email")
  const propertyName = schemaProperty.includes(":")
    ? schemaProperty.split(":")[1]
    : schemaProperty;

  return getValidationPattern(propertyName);
}

/**
 * Validate a value against a PropertyShape
 */
export function validateValue(
  shape: SHACLPropertyShape,
  value: any
): { isValid: boolean; errorMessage?: string } {
  // Check required constraint
  if (isRequired(shape)) {
    if (value === null || value === undefined || (typeof value === "string" && !value.trim())) {
      return { isValid: false, errorMessage: shape["sh:message"] };
    }
  }

  // If value is empty and field is optional, it's valid
  if (value === null || value === undefined || (typeof value === "string" && !value.trim())) {
    return { isValid: true };
  }

  // Check pattern constraint
  if (shape["sh:pattern"] && typeof value === "string") {
    const regex = new RegExp(shape["sh:pattern"]);
    if (!regex.test(value)) {
      return { isValid: false, errorMessage: shape["sh:message"] };
    }
  }

  // Check allowed values constraint
  if (shape["sh:in"]) {
    const allowedValues = getAllowedValues(shape);
    if (allowedValues && !allowedValues.includes(value)) {
      return { isValid: false, errorMessage: shape["sh:message"] };
    }
  }

  // Check length constraints
  if (typeof value === "string") {
    if (shape["sh:minLength"] !== undefined && value.length < shape["sh:minLength"]) {
      return { isValid: false, errorMessage: shape["sh:message"] };
    }
    if (shape["sh:maxLength"] !== undefined && value.length > shape["sh:maxLength"]) {
      return { isValid: false, errorMessage: shape["sh:message"] };
    }
  }

  return { isValid: true };
}
