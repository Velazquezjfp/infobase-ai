import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Case, Document, FormField, ChatMessage } from '@/types/case';
import { mockCase, initialFormFields, initialChatMessages, sampleCases, sampleCaseFormData, createNewCase } from '@/data/mockData';

interface AppContextType {
  user: string | null;
  setUser: (user: string | null) => void;
  // Multi-case support
  cases: Case[];
  setCases: (cases: Case[]) => void;
  currentCase: Case;
  setCurrentCase: (caseData: Case) => void;
  switchCase: (caseId: string) => void;
  addNewCase: (name: string) => Case;
  searchCases: (query: string) => Case[];
  // Document and view
  selectedDocument: Document | null;
  setSelectedDocument: (doc: Document | null) => void;
  viewMode: 'document' | 'form' | 'metadata';
  setViewMode: (mode: 'document' | 'form' | 'metadata') => void;
  // Form fields per case
  formFields: FormField[];
  setFormFields: (fields: FormField[]) => void;
  updateFormField: (id: string, value: string) => void;
  allCaseFormData: Record<string, FormField[]>;
  // Chat
  chatMessages: ChatMessage[];
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  // UI state
  highlightedFolder: string | null;
  setHighlightedFolder: (folderId: string | null) => void;
  isAdminMode: boolean;
  setIsAdminMode: (mode: boolean) => void;
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: (collapsed: boolean) => void;
  toggleFolder: (folderId: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  const [cases, setCases] = useState<Case[]>(sampleCases);
  const [currentCase, setCurrentCase] = useState<Case>(mockCase);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [viewMode, setViewMode] = useState<'document' | 'form' | 'metadata'>('form');
  const [allCaseFormData, setAllCaseFormData] = useState<Record<string, FormField[]>>(sampleCaseFormData);
  const [formFields, setFormFields] = useState<FormField[]>(initialFormFields);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(initialChatMessages);
  const [highlightedFolder, setHighlightedFolder] = useState<string | null>(null);
  const [isAdminMode, setIsAdminMode] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const updateFormField = (id: string, value: string) => {
    setFormFields(fields =>
      fields.map(field =>
        field.id === id ? { ...field, value } : field
      )
    );
    // Also update in allCaseFormData
    setAllCaseFormData(prev => ({
      ...prev,
      [currentCase.id]: prev[currentCase.id]?.map(field =>
        field.id === id ? { ...field, value } : field
      ) || [],
    }));
  };

  const switchCase = (caseId: string) => {
    const targetCase = cases.find(c => c.id === caseId);
    if (targetCase) {
      // Save current form data
      setAllCaseFormData(prev => ({
        ...prev,
        [currentCase.id]: formFields,
      }));
      // Switch to new case
      setCurrentCase(targetCase);
      setFormFields(allCaseFormData[caseId] || initialFormFields.map(f => ({ ...f, value: '' })));
      setSelectedDocument(null);
      setViewMode('form');
      // Reset chat for new case
      setChatMessages([{
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `Switched to case ${targetCase.id}: ${targetCase.name}.\n\nHow can I assist you with this case?`,
        timestamp: new Date().toISOString(),
      }]);
    }
  };

  const addNewCase = (name: string): Case => {
    const newCase = createNewCase(name);
    setCases(prev => [...prev, newCase]);
    // Initialize form data for new case
    setAllCaseFormData(prev => ({
      ...prev,
      [newCase.id]: initialFormFields.map(f => ({ ...f, value: '' })),
    }));
    return newCase;
  };

  const searchCases = (query: string): Case[] => {
    if (!query.trim()) return cases;
    const lowerQuery = query.toLowerCase();
    return cases.filter(c => {
      // Search in case ID and name
      if (c.id.toLowerCase().includes(lowerQuery)) return true;
      if (c.name.toLowerCase().includes(lowerQuery)) return true;
      // Search in form fields for this case
      const caseFormData = allCaseFormData[c.id];
      if (caseFormData) {
        return caseFormData.some(field => 
          field.value?.toLowerCase().includes(lowerQuery)
        );
      }
      return false;
    });
  };

  const addChatMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg-${Date.now()}`,
      timestamp: new Date().toISOString(),
    };
    setChatMessages(prev => [...prev, newMessage]);
  };

  const toggleFolder = (folderId: string) => {
    setCurrentCase(prev => ({
      ...prev,
      folders: prev.folders.map(folder =>
        folder.id === folderId
          ? { ...folder, isExpanded: !folder.isExpanded }
          : folder
      ),
    }));
  };

  return (
    <AppContext.Provider
      value={{
        user,
        setUser,
        cases,
        setCases,
        currentCase,
        setCurrentCase,
        switchCase,
        addNewCase,
        searchCases,
        selectedDocument,
        setSelectedDocument,
        viewMode,
        setViewMode,
        formFields,
        setFormFields,
        updateFormField,
        allCaseFormData,
        chatMessages,
        addChatMessage,
        highlightedFolder,
        setHighlightedFolder,
        isAdminMode,
        setIsAdminMode,
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        toggleFolder,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
