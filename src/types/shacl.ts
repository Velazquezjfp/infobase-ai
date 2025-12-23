/**
 * SHACL (Shapes Constraint Language) TypeScript Interfaces
 *
 * These interfaces mirror the Python dataclasses in backend/schemas/shacl.py
 * and represent SHACL shapes in JSON-LD format for form field metadata.
 *
 * References:
 * - SHACL Spec: https://www.w3.org/TR/shacl/
 * - JSON-LD: https://json-ld.org/
 * - Schema.org: https://schema.org/
 */

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
    required?: boolean;
    allowedValues?: string[];
    pattern?: string;
    minLength?: number;
    maxLength?: number;
  }
): SHACLPropertyShape {
  const shape: SHACLPropertyShape = {
    "@context": SHACL_CONTEXT,
    "@type": "sh:PropertyShape",
    "sh:path": path,
    "sh:datatype": datatype,
    "sh:name": name,
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
