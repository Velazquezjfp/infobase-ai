Requirement Update: Anonymization Service Integration

• Service Trigger: The anonymization service must be implemented as a tool for the AI agent, triggered specifically when a user clicks the "Anonymize" button in the document visualization interface.
• Data Processing (Base64):
    ◦ The system shall convert the target document into a base64 string to be sent as input to the pre-existing anonymization service.
    ◦ The service must return the processed image as a base64 string featuring black boxes (masking) over sensitive data.
• File & Path Management:
    ◦ Despite using base64 for processing, the system must maintain the local file structure by duplicating the file at its original directory path.
    ◦ The system must use the original file path as input to ensure the clone is saved in the correct location (e.g., the certificates or personal data folders).
• Naming Convention: The output file must be saved as a clone of the original with the suffix _anonymized added to the filename (e.g., birth_certificate_anonymized.png).
• Technical Constraints:
    ◦ Privacy: The service must remain self-contained, running its own trained model without calling external services to ensure maximum data security.
    ◦ User Experience: Upon completion, the interface should automatically switch the visualization to show the newly created anonymized document.

This is the swagger information of the external anonymization service which you have to call.
{"components":{"schemas":{"Detection":{"properties":{"confidence":{"description":"Detection confidence score","maximum":1,"minimum":0,"type":"number"},"coordinate":{"description":"Bounding box: [x, y, width, height]","items":{"type":"integer"},"maxItems":4,"minItems":4,"type":"array"}},"type":"object"}}},"info":{"description":"API for detecting and locating PII in identity documents (passports, birth certificates, driving licenses)","title":"Document Anonymization API","version":"1.0.0"},"openapi":"3.0.0","paths":{"/ai-analysis":{"post":{"description":"Detects and returns coordinates of personally identifiable information in document images","parameters":[{"description":"API authentication key","example":"2b5e151428aed2a6aff7158846cf4f2c","in":"header","name":"Secret-Key","required":true,"schema":{"type":"string"}}],"requestBody":{"content":{"application/json":{"schema":{"properties":{"image":{"description":"Base64-encoded image with data URI prefix","example":"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==","type":"string"},"mode":{"description":"Response mode: 'default' returns anonymized image, 'customize'/'none' return coordinates JSON","enum":["default","customize","none"],"example":"default","type":"string"}},"required":["image"],"type":"object"}}},"required":true},"responses":{"200":{"content":{"application/json":{"schema":{"oneOf":[{"description":"Response when mode='default'","properties":{"anonymized_image":{"description":"Base64-encoded PNG image with PII anonymized","example":"data:image/png;base64,iVBORw0KGgo...","type":"string"},"detections_count":{"description":"Total number of PII detections","example":5,"type":"integer"},"mode":{"example":"default","type":"string"}},"type":"object"},{"description":"Response when mode='customize' or unspecified","properties":{"data":{"description":"Detected PII entities with coordinates","example":{"name":[{"confidence":0.95,"coordinate":[120,45,200,30]}],"photo":[{"confidence":1.0,"coordinate":[50,60,150,180]}]},"type":"object"}},"type":"object"}]}}},"description":"Successful response (format depends on mode)"},"400":{"content":{"application/json":{"schema":{"properties":{"error":{"type":"string"}},"type":"object"}}},"description":"Bad request or processing error"},"401":{"description":"Missing or invalid API key"}},"summary":"Analyze document for PII"}}},"servers":[{"description":"Local development server","url":"http://localhost:5000"}]}

I want to use the default mode now.

--------------------------------------------------------------------------------
Updated Implementation & Agent Instructions
• Agent Interaction: The agent should be instructed that "Anonymization is enough" for this phase, prioritizing it over other actions like translation.
• Verification: Ensure the agent tests the "cascading context" to confirm that the service is pulling the correct document from the active folder/case before performing the base64 conversion.

---------------------------------------------------------------------------

1. Also update the viewer to view image.
2. Also give an option to download the anonymized image.