import { Case, SlashCommand, FormField, ChatMessage, Folder } from '@/types/case';

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
];

// Case-type form templates - each case type has its own form schema
// D-002: Integration Course Application form (7 fields)
export const integrationCourseFormTemplate: FormField[] = [
  { id: 'fullName', label: 'Full Name', type: 'text', value: '', required: true },
  { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '', required: true },
  { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: '', required: true },
  { id: 'existingLanguageCertificates', label: 'Existing Language Certificates', type: 'text', value: '' },
  { id: 'coursePreference', label: 'Course Preference', type: 'select', value: '', options: ['Intensive Course', 'Evening Course', 'Weekend Course'] },
  { id: 'currentAddress', label: 'Current Address', type: 'textarea', value: '', required: true },
  { id: 'reasonForApplication', label: 'Reason for Application', type: 'textarea', value: '', required: true },
];

// Asylum Application form - different fields appropriate for asylum cases
export const asylumApplicationFormTemplate: FormField[] = [
  { id: 'fullName', label: 'Full Name', type: 'text', value: '', required: true },
  { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '', required: true },
  { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: '', required: true },
  { id: 'nationality', label: 'Nationality', type: 'text', value: '', required: true },
  { id: 'entryDate', label: 'Date of Entry to Germany', type: 'date', value: '', required: true },
  { id: 'currentAddress', label: 'Current Address', type: 'textarea', value: '', required: true },
  { id: 'reasonForAsylum', label: 'Reason for Asylum Application', type: 'textarea', value: '', required: true },
];

// Family Reunification form - different fields appropriate for family reunification
export const familyReunificationFormTemplate: FormField[] = [
  { id: 'fullName', label: 'Full Name', type: 'text', value: '', required: true },
  { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '', required: true },
  { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: '', required: true },
  { id: 'relationshipType', label: 'Relationship to Sponsor', type: 'select', value: '', options: ['Spouse', 'Child', 'Parent', 'Other'], required: true },
  { id: 'sponsorName', label: 'Sponsor Full Name', type: 'text', value: '', required: true },
  { id: 'currentAddress', label: 'Current Address', type: 'textarea', value: '', required: true },
  { id: 'reasonForReunification', label: 'Reason for Family Reunification', type: 'textarea', value: '', required: true },
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
export const defaultFolderTemplate: Omit<Folder, 'id'>[] = [
  { name: 'Personal Data', documents: [], subfolders: [], isExpanded: true },
  { name: 'Certificates', documents: [], subfolders: [], isExpanded: false },
  { name: 'Integration Course Documents', documents: [], subfolders: [], isExpanded: false },
  { name: 'Applications & Forms', documents: [], subfolders: [], isExpanded: false },
  { name: 'Emails', documents: [], subfolders: [], isExpanded: false },
  { name: 'Additional Evidence', documents: [], subfolders: [], isExpanded: false },
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
        { id: 'doc-1', name: 'Birth_Certificate.pdf', type: 'pdf', size: '245 KB', uploadedAt: '2024-01-15', metadata: { documentType: 'Birth Certificate', issuer: 'Kabul Civil Registry', language: 'Dari' } },
        { id: 'doc-2', name: 'Passport_Scan.pdf', type: 'pdf', size: '1.2 MB', uploadedAt: '2024-01-15', metadata: { documentType: 'Passport', expiryDate: '2028-05-20' } },
      ],
      subfolders: [],
    },
    {
      id: 'certificates',
      name: 'Certificates',
      isExpanded: false,
      documents: [
        { id: 'doc-3', name: 'Language_Certificate_A1.pdf', type: 'pdf', size: '156 KB', uploadedAt: '2024-01-16', metadata: { level: 'A1', institution: 'Goethe Institut' } },
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
        { id: 'doc-4', name: 'Integration_Application.json', type: 'json', size: '12 KB', uploadedAt: '2024-01-17', metadata: { status: 'draft', version: '1.0' } },
      ],
      subfolders: [],
    },
    {
      id: 'emails',
      name: 'Emails',
      isExpanded: false,
      documents: [
        { id: 'doc-6', name: 'Confirmation_Email.pdf', type: 'pdf', size: '45 KB', uploadedAt: '2024-01-18', metadata: { from: 'bamf@example.de', subject: 'Application Received' } },
      ],
      subfolders: [],
    },
    {
      id: 'evidence',
      name: 'Additional Evidence',
      isExpanded: false,
      documents: [
        { id: 'doc-5', name: 'School_Transcripts.pdf', type: 'pdf', size: '890 KB', uploadedAt: '2024-01-16', metadata: { documentType: 'Transcript', institution: 'Kabul University' } },
      ],
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
export const sampleCaseFormData: Record<string, FormField[]> = {
  // Integration Course Application - uses integrationCourseFormTemplate (empty form)
  'ACTE-2024-001': integrationCourseFormTemplate,

  // Asylum Application - uses asylumApplicationFormTemplate with sample data
  'ACTE-2024-002': [
    { id: 'fullName', label: 'Full Name', type: 'text', value: 'Ahmed Hassan', required: true },
    { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '1990-05-15', required: true },
    { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: 'Syria', required: true },
    { id: 'nationality', label: 'Nationality', type: 'text', value: 'Syrian', required: true },
    { id: 'entryDate', label: 'Date of Entry to Germany', type: 'date', value: '2024-01-10', required: true },
    { id: 'currentAddress', label: 'Current Address', type: 'textarea', value: 'Berlin, Germany', required: true },
    { id: 'reasonForAsylum', label: 'Reason for Asylum Application', type: 'textarea', value: 'Seeking asylum due to civil conflict in home country', required: true },
  ],

  // Family Reunification - uses familyReunificationFormTemplate with sample data
  'ACTE-2024-003': [
    { id: 'fullName', label: 'Full Name', type: 'text', value: 'Maria Gonzalez', required: true },
    { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '1985-11-22', required: true },
    { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: 'Mexico', required: true },
    { id: 'relationshipType', label: 'Relationship to Sponsor', type: 'select', value: 'Spouse', options: ['Spouse', 'Child', 'Parent', 'Other'], required: true },
    { id: 'sponsorName', label: 'Sponsor Full Name', type: 'text', value: 'Carlos Gonzalez', required: true },
    { id: 'currentAddress', label: 'Current Address', type: 'textarea', value: 'Munich, Germany', required: true },
    { id: 'reasonForReunification', label: 'Reason for Family Reunification', type: 'textarea', value: 'Joining spouse who has permanent residence in Germany', required: true },
  ],
};

export const initialChatMessages: ChatMessage[] = [
  {
    id: 'msg-1',
    role: 'assistant',
    content: 'Welcome to the BAMF Case Management System. I am ready to assist you with case ACTE-2024-001: German Integration Course Application.\n\nYou can use slash commands (/) to perform actions or simply ask me questions about the case.',
    timestamp: new Date().toISOString(),
  },
];
