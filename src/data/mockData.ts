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

export const initialFormFields: FormField[] = [
  { id: 'name', label: 'Full Name', type: 'text', value: '', required: true },
  { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '', required: true },
  { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: '', required: true },
  { id: 'languageCertificates', label: 'Existing Language Certificates', type: 'text', value: '' },
  { id: 'coursePreference', label: 'Course Preference', type: 'select', value: '', options: ['Intensive Course', 'Evening Course', 'Weekend Course', 'Online Course'] },
  { id: 'address', label: 'Current Address', type: 'textarea', value: '', required: true },
  { id: 'reasonForApplication', label: 'Reason for Application', type: 'textarea', value: '', required: true },
];

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

// Sample form data for different cases
export const sampleCaseFormData: Record<string, FormField[]> = {
  'ACTE-2024-001': initialFormFields,
  'ACTE-2024-002': [
    { id: 'name', label: 'Full Name', type: 'text', value: 'Ahmed Hassan', required: true },
    { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '1990-05-15', required: true },
    { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: 'Syria', required: true },
    { id: 'languageCertificates', label: 'Existing Language Certificates', type: 'text', value: 'Arabic Native' },
    { id: 'coursePreference', label: 'Course Preference', type: 'select', value: 'Intensive Course', options: ['Intensive Course', 'Evening Course', 'Weekend Course', 'Online Course'] },
    { id: 'address', label: 'Current Address', type: 'textarea', value: 'Berlin, Germany', required: true },
    { id: 'reasonForApplication', label: 'Reason for Application', type: 'textarea', value: 'Seeking asylum and integration support', required: true },
  ],
  'ACTE-2024-003': [
    { id: 'name', label: 'Full Name', type: 'text', value: 'Maria Gonzalez', required: true },
    { id: 'birthDate', label: 'Date of Birth', type: 'date', value: '1985-11-22', required: true },
    { id: 'countryOfOrigin', label: 'Country of Origin', type: 'text', value: 'Mexico', required: true },
    { id: 'languageCertificates', label: 'Existing Language Certificates', type: 'text', value: 'Spanish Native, English B2' },
    { id: 'coursePreference', label: 'Course Preference', type: 'select', value: 'Evening Course', options: ['Intensive Course', 'Evening Course', 'Weekend Course', 'Online Course'] },
    { id: 'address', label: 'Current Address', type: 'textarea', value: 'Munich, Germany', required: true },
    { id: 'reasonForApplication', label: 'Reason for Application', type: 'textarea', value: 'Family reunification with spouse', required: true },
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
