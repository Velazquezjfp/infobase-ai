import { Case, SlashCommand, FormField, ChatMessage, Folder, HierarchicalSlashCommand, SlashCommandArgument } from '@/types/case';
import { SHACL_CONTEXT, type SHACLPropertyShape } from '@/types/shacl';

export const slashCommands: SlashCommand[] = [
  { command: '/addDocument', label: 'Add Document', description: 'Upload a new document to the case', icon: 'Plus' },
  { command: '/convert', label: 'Convert', description: 'Convert document to PDF, JSON, or XML', icon: 'FileOutput' },
  { command: '/search', label: 'Search', description: 'Search across all case documents', icon: 'Search' },
  { command: '/anonymize', label: 'Anonymize', description: 'Remove personal data from document', icon: 'EyeOff' },
  { command: '/translate', label: 'Translate', description: 'Translate document to German', icon: 'Languages' },
  { command: '/validateCase', label: 'Validate Case', description: 'Check for missing documents', icon: 'CheckCircle' },
  { command: '/changeActeName', label: 'Rename Case', description: 'Change the case name', icon: 'Edit' },
  { command: '/switchCase', label: 'Switch Case', description: 'Open a different case', icon: 'FolderOpen' },
  { command: '/transcribe', label: 'Transcribe', description: 'Extract text from document', icon: 'FileText' },
  { command: '/generateEmail', label: 'Generate Email', description: 'Create notification email', icon: 'Mail' },
  { command: '/extractMetadata', label: 'Extract Metadata', description: 'Extract document metadata', icon: 'Database' },
  { command: '/fillForm', label: 'Fill Form', description: 'Extract data from document to form fields', icon: 'FileInput' },
  // S5-017: Context modification commands
  { command: '/Aktenkontext', label: 'Aktenkontext', description: 'Modify case context (rules, documents)', icon: 'Settings' },
  { command: '/removeAktenkontext', label: 'Remove Context Rule', description: 'Remove a custom context rule', icon: 'Trash2' },
];

/**
 * S5-017: Hierarchical slash commands for context modification
 * These commands have nested argument structures for guided input
 */
export const hierarchicalSlashCommands: HierarchicalSlashCommand[] = [
  {
    command: '/Aktenkontext',
    label: 'Aktenkontext',
    description: 'Modify case context (rules, documents)',
    icon: 'Settings',
    arguments: [
      {
        value: 'Regeln',
        label: 'Regeln',
        description: 'Add validation rules to the case',
        children: [
          {
            value: 'Ordner',
            label: 'Ordner',
            description: 'Folder-specific validation rule',
            children: [], // Will be populated dynamically with folder names
            requiresInput: true,
            placeholder: '"Rule description"'
          },
          {
            value: 'Dateityp',
            label: 'Dateityp',
            description: 'File type validation rule',
            requiresInput: true,
            placeholder: '"Only PDF files allowed"'
          },
          {
            value: 'Inhalt',
            label: 'Inhalt',
            description: 'Content validation rule',
            requiresInput: true,
            placeholder: '"Document must contain signature"'
          },
          {
            value: 'Metadaten',
            label: 'Metadaten',
            description: 'Metadata validation rule',
            requiresInput: true,
            placeholder: '"Document must have author field"'
          },
          {
            value: 'Vollständigkeit',
            label: 'Vollständigkeit',
            description: 'Completeness validation rule',
            requiresInput: true,
            placeholder: '"All pages must be present"'
          }
        ]
      },
      {
        value: 'Dokumente',
        label: 'Dokumente',
        description: 'Add required document to the case',
        requiresInput: true,
        placeholder: '"An anonymized version of the passport is necessary under Personal Data"'
      }
    ]
  },
  {
    command: '/removeAktenkontext',
    label: 'Remove Context Rule',
    description: 'Remove a custom context rule',
    icon: 'Trash2',
    isDynamic: true,
    dynamicSource: 'customRules',
    arguments: [] // Populated dynamically with existing rules
  }
];

/**
 * Get folder names from a case for dynamic command arguments
 */
export const getFolderArguments = (folders: Folder[]): SlashCommandArgument[] => {
  return folders.map(folder => ({
    value: folder.name,
    label: folder.name,
    description: `Add rule for ${folder.name} folder`,
    requiresInput: true,
    placeholder: '"Rule description"'
  }));
};

// Case-type form templates - each case type has its own form schema
// D-002: Integration Course Application form (7 fields)
// S2-003: Updated with SHACL/JSON-LD semantic metadata
export const integrationCourseFormTemplate: FormField[] = [
  {
    id: 'fullName',
    label: 'Full Name',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:name',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Full Name',
      'sh:description': 'The applicant\'s full legal name',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'birthDate',
    label: 'Date of Birth',
    type: 'date',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:birthDate',
      'sh:datatype': 'xsd:date',
      'sh:name': 'Date of Birth',
      'sh:description': 'The applicant\'s date of birth',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'countryOfOrigin',
    label: 'Country of Origin',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:nationality',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Country of Origin',
      'sh:description': 'The applicant\'s country of origin or nationality',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'existingLanguageCertificates',
    label: 'Existing Language Certificates',
    type: 'text',
    value: '',
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:knowsLanguage',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Existing Language Certificates',
      'sh:description': 'Any existing language certificates the applicant holds',
      'sh:maxCount': 1,
    },
  },
  {
    id: 'coursePreference',
    label: 'Course Preference',
    type: 'select',
    value: '',
    options: ['Intensive Course', 'Evening Course', 'Weekend Course'],
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:courseCode',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Course Preference',
      'sh:description': 'Preferred course schedule type',
      'sh:maxCount': 1,
      'sh:in': { '@list': ['Intensive Course', 'Evening Course', 'Weekend Course'] },
    },
  },
  {
    id: 'currentAddress',
    label: 'Current Address',
    type: 'textarea',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:address',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Current Address',
      'sh:description': 'The applicant\'s current residential address in Germany',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'reasonForApplication',
    label: 'Reason for Application',
    type: 'textarea',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:description',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Reason for Application',
      'sh:description': 'The reason for applying to the integration course',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
];

// Asylum Application form - different fields appropriate for asylum cases
// S2-003: Updated with SHACL/JSON-LD semantic metadata
export const asylumApplicationFormTemplate: FormField[] = [
  {
    id: 'fullName',
    label: 'Full Name',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:name',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Full Name',
      'sh:description': 'The applicant\'s full legal name',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'birthDate',
    label: 'Date of Birth',
    type: 'date',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:birthDate',
      'sh:datatype': 'xsd:date',
      'sh:name': 'Date of Birth',
      'sh:description': 'The applicant\'s date of birth',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'countryOfOrigin',
    label: 'Country of Origin',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:nationality',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Country of Origin',
      'sh:description': 'The applicant\'s country of origin',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'nationality',
    label: 'Nationality',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:nationality',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Nationality',
      'sh:description': 'The applicant\'s current nationality',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'entryDate',
    label: 'Date of Entry to Germany',
    type: 'date',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:arrivalTime',
      'sh:datatype': 'xsd:date',
      'sh:name': 'Date of Entry to Germany',
      'sh:description': 'The date when the applicant entered Germany',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'currentAddress',
    label: 'Current Address',
    type: 'textarea',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:address',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Current Address',
      'sh:description': 'The applicant\'s current residential address in Germany',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'reasonForAsylum',
    label: 'Reason for Asylum Application',
    type: 'textarea',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:description',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Reason for Asylum Application',
      'sh:description': 'The reason for seeking asylum',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
];

// Family Reunification form - different fields appropriate for family reunification
// S2-003: Updated with SHACL/JSON-LD semantic metadata
export const familyReunificationFormTemplate: FormField[] = [
  {
    id: 'fullName',
    label: 'Full Name',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:name',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Full Name',
      'sh:description': 'The applicant\'s full legal name',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'birthDate',
    label: 'Date of Birth',
    type: 'date',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:birthDate',
      'sh:datatype': 'xsd:date',
      'sh:name': 'Date of Birth',
      'sh:description': 'The applicant\'s date of birth',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'countryOfOrigin',
    label: 'Country of Origin',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:nationality',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Country of Origin',
      'sh:description': 'The applicant\'s country of origin',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'relationshipType',
    label: 'Relationship to Sponsor',
    type: 'select',
    value: '',
    options: ['Spouse', 'Child', 'Parent', 'Other'],
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:familyName',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Relationship to Sponsor',
      'sh:description': 'The family relationship between applicant and sponsor',
      'sh:minCount': 1,
      'sh:maxCount': 1,
      'sh:in': { '@list': ['Spouse', 'Child', 'Parent', 'Other'] },
    },
  },
  {
    id: 'sponsorName',
    label: 'Sponsor Full Name',
    type: 'text',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:sponsor',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Sponsor Full Name',
      'sh:description': 'The full legal name of the sponsoring family member',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'currentAddress',
    label: 'Current Address',
    type: 'textarea',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:address',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Current Address',
      'sh:description': 'The applicant\'s current residential address',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
  {
    id: 'reasonForReunification',
    label: 'Reason for Family Reunification',
    type: 'textarea',
    value: '',
    required: true,
    shaclMetadata: {
      '@context': SHACL_CONTEXT,
      '@type': 'sh:PropertyShape',
      'sh:path': 'schema:description',
      'sh:datatype': 'xsd:string',
      'sh:name': 'Reason for Family Reunification',
      'sh:description': 'The reason for seeking family reunification',
      'sh:minCount': 1,
      'sh:maxCount': 1,
    },
  },
];

// Maps case type identifiers to their form templates
export const caseFormTemplates: Record<string, FormField[]> = {
  'integration_course': integrationCourseFormTemplate,
  'asylum_application': asylumApplicationFormTemplate,
  'family_reunification': familyReunificationFormTemplate,
};

// Default form fields - uses Integration Course template as default for backwards compatibility
export const initialFormFields: FormField[] = integrationCourseFormTemplate;

// Default folder template for new cases
// S4-001: Added 'Uploads' folder for drag-and-drop file upload feature
export const defaultFolderTemplate: Omit<Folder, 'id'>[] = [
  { name: 'Personal Data', documents: [], subfolders: [], isExpanded: true },
  { name: 'Certificates', documents: [], subfolders: [], isExpanded: false },
  { name: 'Integration Course Documents', documents: [], subfolders: [], isExpanded: false },
  { name: 'Applications & Forms', documents: [], subfolders: [], isExpanded: false },
  { name: 'Emails', documents: [], subfolders: [], isExpanded: false },
  { name: 'Additional Evidence', documents: [], subfolders: [], isExpanded: false },
  { name: 'Uploads', documents: [], subfolders: [], isExpanded: false },
];

export const createNewCase = (name: string, id?: string): Case => {
  const caseId = id || `ACTE-${new Date().getFullYear()}-${String(Date.now()).slice(-3)}`;
  return {
    id: caseId,
    name,
    createdAt: new Date().toISOString().split('T')[0],
    status: 'open',
    folders: defaultFolderTemplate.map((folder, index): Folder => ({
      ...folder,
      id: `${caseId}-folder-${index}`,
    })),
  };
};

export const mockCase: Case = {
  id: 'ACTE-2024-001',
  name: 'German Integration Course Application',
  createdAt: '2024-01-15',
  status: 'open',
  folders: [
    {
      id: 'personal-data',
      name: 'Personal Data',
      isExpanded: true,
      documents: [
        { id: 'doc-1', name: 'Geburtsurkunde.jpg', type: 'jpg', size: '261 KB', uploadedAt: '2024-01-15', metadata: { documentType: 'Birth Certificate', issuer: 'Kabul Civil Registry', language: 'German' }, caseId: 'ACTE-2024-001', folderId: 'personal-data' },
        { id: 'doc-2', name: 'Personalausweis.png', type: 'png', size: '255 KB', uploadedAt: '2024-01-15', metadata: { documentType: 'ID Card', issuer: 'German authorities' }, caseId: 'ACTE-2024-001', folderId: 'personal-data' },
        { id: 'doc-3', name: 'Aufenthalstitel.png', type: 'png', size: '815 KB', uploadedAt: '2024-01-15', metadata: { documentType: 'Residence Permit' }, caseId: 'ACTE-2024-001', folderId: 'personal-data' },
      ],
      subfolders: [],
    },
    {
      id: 'certificates',
      name: 'Certificates',
      isExpanded: false,
      documents: [
        { id: 'doc-4', name: 'Sprachzeugnis-Zertifikat.pdf', type: 'pdf', size: '149 KB', uploadedAt: '2024-01-16', metadata: { level: 'A2', institution: 'Goethe Institut', documentType: 'Language Certificate' }, caseId: 'ACTE-2024-001', folderId: 'certificates' },
      ],
      subfolders: [],
    },
    {
      id: 'integration-docs',
      name: 'Integration Course Documents',
      isExpanded: false,
      documents: [],
      subfolders: [],
    },
    {
      id: 'applications',
      name: 'Applications & Forms',
      isExpanded: false,
      documents: [
        { id: 'doc-5', name: 'Anmeldeformular.pdf', type: 'pdf', size: '101 KB', uploadedAt: '2024-01-17', metadata: { status: 'draft', documentType: 'Integration Course Application Form' }, caseId: 'ACTE-2024-001', folderId: 'applications' },
      ],
      subfolders: [],
    },
    {
      id: 'emails',
      name: 'Emails',
      isExpanded: false,
      documents: [
        { id: 'doc-6', name: 'Email.eml', type: 'eml', size: '20 KB', uploadedAt: '2024-01-18', metadata: { from: 'bamf@example.de', subject: 'Application Confirmation', language: 'Arabic', documentType: 'Email' }, caseId: 'ACTE-2024-001', folderId: 'emails' },
      ],
      subfolders: [],
    },
    {
      id: 'evidence',
      name: 'Additional Evidence',
      isExpanded: false,
      documents: [
        { id: 'doc-7', name: 'Notenspiegel.pdf', type: 'pdf', size: '79 KB', uploadedAt: '2024-01-16', metadata: { documentType: 'University Transcript', institution: 'Kabul University' }, caseId: 'ACTE-2024-001', folderId: 'evidence' },
      ],
      subfolders: [],
    },
    {
      id: 'uploads',
      name: 'Uploads',
      isExpanded: false,
      documents: [],
      subfolders: [],
    },
  ],
};

// Additional sample cases for search demo
export const sampleCases: Case[] = [
  mockCase,
  {
    id: 'ACTE-2024-002',
    name: 'Asylum Application - Ahmed Hassan',
    createdAt: '2024-02-10',
    status: 'pending',
    folders: defaultFolderTemplate.map((folder, index): Folder => ({
      ...folder,
      id: `ACTE-2024-002-folder-${index}`,
    })),
  },
  {
    id: 'ACTE-2024-003',
    name: 'Family Reunification - Maria Gonzalez',
    createdAt: '2024-03-05',
    status: 'open',
    folders: defaultFolderTemplate.map((folder, index): Folder => ({
      ...folder,
      id: `ACTE-2024-003-folder-${index}`,
    })),
  },
];

// Sample form data for different cases - each case uses its appropriate form template
// S2-003: All form data includes SHACL metadata for semantic interoperability
export const sampleCaseFormData: Record<string, FormField[]> = {
  // Integration Course Application - uses integrationCourseFormTemplate (empty form)
  'ACTE-2024-001': integrationCourseFormTemplate,

  // Asylum Application - uses asylumApplicationFormTemplate with sample data and SHACL metadata
  'ACTE-2024-002': asylumApplicationFormTemplate.map((field, index) => {
    const sampleValues: Record<string, string> = {
      fullName: 'Ahmed Hassan',
      birthDate: '1990-05-15',
      countryOfOrigin: 'Syria',
      nationality: 'Syrian',
      entryDate: '2024-01-10',
      currentAddress: 'Berlin, Germany',
      reasonForAsylum: 'Seeking asylum due to civil conflict in home country',
    };
    return { ...field, value: sampleValues[field.id] || field.value };
  }),

  // Family Reunification - uses familyReunificationFormTemplate with sample data and SHACL metadata
  'ACTE-2024-003': familyReunificationFormTemplate.map((field, index) => {
    const sampleValues: Record<string, string> = {
      fullName: 'Maria Gonzalez',
      birthDate: '1985-11-22',
      countryOfOrigin: 'Mexico',
      relationshipType: 'Spouse',
      sponsorName: 'Carlos Gonzalez',
      currentAddress: 'Munich, Germany',
      reasonForReunification: 'Joining spouse who has permanent residence in Germany',
    };
    return { ...field, value: sampleValues[field.id] || field.value };
  }),
};

// S5-014: Function to generate initial messages based on language
export const getInitialChatMessages = (language: 'de' | 'en' = 'de', caseId: string = 'ACTE-2024-001', caseName: string = 'German Integration Course Application'): ChatMessage[] => {
  const casePrefix = language === 'de' ? 'Akte' : 'Case';
  const translatedCaseId = caseId.replace('ACTE', casePrefix);

  const messages = {
    de: `Willkommen beim BAMF Aktenverwaltungssystem. Ich bin bereit, Sie bei der ${translatedCaseId} zu unterstützen: ${caseName}.\n\nSie können Slash-Befehle (/) verwenden, um Aktionen auszuführen, oder mir einfach Fragen zur Akte stellen.`,
    en: `Welcome to the BAMF Case Management System. I am ready to assist you with ${translatedCaseId}: ${caseName}.\n\nYou can use slash commands (/) to perform actions or simply ask me questions about the case.`
  };

  return [
    {
      id: 'msg-1',
      role: 'assistant',
      content: messages[language],
      timestamp: new Date().toISOString(),
    },
  ];
};

// Keep for backwards compatibility, defaulting to German
export const initialChatMessages: ChatMessage[] = getInitialChatMessages('de');
