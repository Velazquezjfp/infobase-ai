import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { Case, Document, FormField, ChatMessage, FormSuggestions, SuggestedValue } from '@/types/case';
import { mockCase, initialFormFields, initialChatMessages, getInitialChatMessages, sampleCases, sampleCaseFormData, createNewCase } from '@/data/mockData';
import { WebSocketState, ConnectionStatus, WebSocketMessage, AnonymizationResponse } from '@/types/websocket';
import { SearchHighlight, SemanticSearchRequest, SemanticSearchResponse } from '@/types/search';
import { saveToLocalStorage, loadFromLocalStorage } from '@/lib/localStorage';
import { useToast } from '@/hooks/use-toast';
import i18n from '@/i18n/config';

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
  // S5-006: Render selection
  selectedRender: string | null;
  setSelectedRender: (renderId: string | null) => void;
  selectDocumentWithRender: (doc: Document, renderId?: string) => void;
  // S5-003: Update document content (for PDF text extraction)
  updateSelectedDocumentContent: (content: string) => void;
  // Form fields per case
  formFields: FormField[];
  setFormFields: (fields: FormField[]) => void;
  updateFormField: (id: string, value: string) => void;
  allCaseFormData: Record<string, FormField[]>;
  // Chat
  chatMessages: ChatMessage[];
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  sendChatMessage: (content: string, documentContent?: string) => void;
  // WebSocket
  wsConnection: WebSocket | null;
  wsStatus: ConnectionStatus;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  isTyping: boolean;
  // Anonymization
  isAnonymizing: boolean;
  setIsAnonymizing: (isAnonymizing: boolean) => void;
  // Translation (S5-004)
  isTranslating: boolean;
  setIsTranslating: (isTranslating: boolean) => void;
  // Document management (S4-001, S4-002)
  addDocumentToFolder: (caseId: string, folderId: string, document: Document) => void;
  removeDocumentFromFolder: (caseId: string, folderId: string, documentId: string) => void;
  refreshDocuments: () => void;
  // UI state
  highlightedFolder: string | null;
  setHighlightedFolder: (folderId: string | null) => void;
  isAdminMode: boolean;
  setIsAdminMode: (mode: boolean) => void;
  showAdminPanel: boolean;
  setShowAdminPanel: (show: boolean) => void;
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: (collapsed: boolean) => void;
  toggleFolder: (folderId: string) => void;
  // S5-002: Form suggestions
  formSuggestions: FormSuggestions;
  acceptSuggestion: (fieldId: string) => void;
  rejectSuggestion: (fieldId: string) => void;
  // S5-014: Language toggle
  currentLanguage: 'de' | 'en';
  setLanguage: (lang: 'de' | 'en') => void;
  // S5-003: Semantic search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchHighlights: SearchHighlight[];
  setSearchHighlights: (highlights: SearchHighlight[]) => void;
  activeHighlightIndex: number;
  setActiveHighlightIndex: (index: number) => void;
  isSearching: boolean;
  performSemanticSearch: (query: string, documentId: string) => Promise<void>;
  clearSearch: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const { toast } = useToast();

  // Initialize state with localStorage data (with fallback to defaults)
  const [user, setUserState] = useState<string | null>(() => {
    const stored = loadFromLocalStorage<string>('bamf_user');
    if (stored) {
      console.log('Loaded user from localStorage:', stored);
      return stored;
    }
    return null;
  });

  // Wrapper to persist user to localStorage
  const setUser = (newUser: string | null) => {
    setUserState(newUser);
    if (newUser) {
      saveToLocalStorage('bamf_user', newUser);
    } else {
      localStorage.removeItem('bamf_user');
    }
  };
  const [cases, setCases] = useState<Case[]>(sampleCases);
  const [currentCase, setCurrentCase] = useState<Case>(mockCase);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [viewMode, setViewMode] = useState<'document' | 'form' | 'metadata'>('form');

  // S5-006: Selected render state
  const [selectedRender, setSelectedRender] = useState<string | null>(null);

  // Load form data from localStorage with fallback to defaults
  const [allCaseFormData, setAllCaseFormData] = useState<Record<string, FormField[]>>(() => {
    const stored = loadFromLocalStorage<Record<string, FormField[]>>('bamf_case_form_data');
    if (stored) {
      console.log('Loaded case form data from localStorage');
      return stored;
    }
    return sampleCaseFormData;
  });

  // Load form fields from localStorage with fallback to defaults
  const [formFields, setFormFields] = useState<FormField[]>(() => {
    const stored = loadFromLocalStorage<FormField[]>('bamf_form_fields');
    if (stored) {
      console.log('Loaded form fields from localStorage');
      return stored;
    }
    return initialFormFields;
  });

  // S5-014: Initialize chat messages with language-aware welcome message
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(() => {
    const storedLanguage = localStorage.getItem('bamf_language');
    const language = (storedLanguage === 'en' || storedLanguage === 'de') ? storedLanguage : 'de';
    return getInitialChatMessages(language);
  });
  const [highlightedFolder, setHighlightedFolder] = useState<string | null>(null);
  const [isAdminMode, setIsAdminMode] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // WebSocket state
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [wsStatus, setWsStatus] = useState<ConnectionStatus>('disconnected');
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const isStreamingRef = useRef(false);  // Ref to track streaming state (avoids closure issues)
  const [isTyping, setIsTyping] = useState(false);
  const [isAnonymizing, setIsAnonymizing] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);  // S5-004: Translation state

  // S5-002: Form suggestions state
  const [formSuggestions, setFormSuggestions] = useState<FormSuggestions>({});
  const [dismissedSuggestions, setDismissedSuggestions] = useState<Set<string>>(new Set());

  // S5-014: Language state - load from localStorage, default to 'de'
  const [currentLanguage, setCurrentLanguage] = useState<'de' | 'en'>(() => {
    const stored = localStorage.getItem('bamf_language');
    return (stored === 'en' || stored === 'de') ? stored : 'de';
  });

  // S5-003: Search state
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchHighlights, setSearchHighlights] = useState<SearchHighlight[]>([]);
  const [activeHighlightIndex, setActiveHighlightIndex] = useState<number>(0);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  // S5-014: Language setter function
  const setLanguage = (lang: 'de' | 'en') => {
    setCurrentLanguage(lang);
    localStorage.setItem('bamf_language', lang);
    i18n.changeLanguage(lang);

    // Update the initial welcome message if it exists (first message with id 'msg-1')
    setChatMessages(messages => {
      if (messages.length > 0 && messages[0].id === 'msg-1') {
        const newInitialMessages = getInitialChatMessages(lang, currentCase.id, currentCase.name);
        return [newInitialMessages[0], ...messages.slice(1)];
      }
      return messages;
    });
  };

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

    // S5-002: Clear suggestion for this field if it exists
    setFormSuggestions(prev => {
      const updated = { ...prev };
      delete updated[id];
      return updated;
    });
  };

  // S5-002: Accept a suggested value
  const acceptSuggestion = (fieldId: string) => {
    const suggestion = formSuggestions[fieldId];
    if (!suggestion) return;

    // Get field label for chat message
    const field = formFields.find(f => f.id === fieldId);
    const fieldLabel = field?.label || fieldId;

    // Update the form field with suggested value
    updateFormField(fieldId, suggestion.value);

    // Remove suggestion from state
    setFormSuggestions(prev => {
      const updated = { ...prev };
      delete updated[fieldId];
      return updated;
    });

    // Add confirmation chat message with i18n
    addChatMessage({
      role: 'assistant',
      content: `✅ ${i18n.t('formSuggestions.accepted', { fieldLabel, value: suggestion.value })}`,
    });

    toast({
      title: i18n.t('formSuggestions.acceptedTitle'),
      description: i18n.t('formSuggestions.acceptedDescription', { fieldLabel }),
    });
  };

  // S5-002: Reject a suggested value
  const rejectSuggestion = (fieldId: string) => {
    const suggestion = formSuggestions[fieldId];
    if (!suggestion) return;

    // Get field label for chat message
    const field = formFields.find(f => f.id === fieldId);
    const fieldLabel = field?.label || fieldId;

    // Add to dismissed set (persists until navigation)
    setDismissedSuggestions(prev => new Set(prev).add(fieldId));

    // Remove suggestion from state
    setFormSuggestions(prev => {
      const updated = { ...prev };
      delete updated[fieldId];
      return updated;
    });

    // Add confirmation chat message with i18n
    addChatMessage({
      role: 'assistant',
      content: `❌ ${i18n.t('formSuggestions.rejected', { fieldLabel })}`,
    });

    toast({
      title: i18n.t('formSuggestions.rejectedTitle'),
      description: i18n.t('formSuggestions.rejectedDescription', { fieldLabel }),
    });
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

  // S5-006: Select document with optional render
  const selectDocumentWithRender = (doc: Document, renderId?: string) => {
    setSelectedDocument(doc);
    // If no renderId provided, default to 'original' if renders exist
    if (!renderId && doc.renders && doc.renders.length > 0) {
      const originalRender = doc.renders.find(r => r.type === 'original');
      setSelectedRender(originalRender?.id || null);
    } else {
      setSelectedRender(renderId || null);
    }
  };

  // S5-003: Update selected document content (for PDF text extraction)
  const updateSelectedDocumentContent = (content: string) => {
    if (selectedDocument) {
      const updatedDoc = { ...selectedDocument, content };
      setSelectedDocument(updatedDoc);

      // Also update the document in currentCase to ensure persistence
      setCurrentCase(prev => ({
        ...prev,
        folders: prev.folders.map(folder => ({
          ...folder,
          documents: folder.documents.map(doc =>
            doc.id === selectedDocument.id ? updatedDoc : doc
          ),
        })),
      }));
    }
  };

  // Document management functions (S4-001)
  const addDocumentToFolder = (caseId: string, folderId: string, document: Document) => {
    // Update the cases array
    setCases(prevCases =>
      prevCases.map(c =>
        c.id === caseId
          ? {
              ...c,
              folders: c.folders.map(folder =>
                folder.id === folderId || folder.name.toLowerCase() === folderId.toLowerCase()
                  ? { ...folder, documents: [...folder.documents, document] }
                  : folder
              ),
            }
          : c
      )
    );

    // If this is the current case, update it as well
    if (currentCase.id === caseId) {
      setCurrentCase(prev => ({
        ...prev,
        folders: prev.folders.map(folder =>
          folder.id === folderId || folder.name.toLowerCase() === folderId.toLowerCase()
            ? { ...folder, documents: [...folder.documents, document] }
            : folder
        ),
      }));

      // S5-007: Sync with backend after a short delay
      setTimeout(() => {
        loadDocumentsFromBackend(caseId);
      }, 500);
    }

    console.log(`Document ${document.name} added to folder ${folderId} in case ${caseId}`);
  };

  // Document deletion function (S4-002)
  const removeDocumentFromFolder = (caseId: string, folderId: string, documentId: string) => {
    // Update the cases array
    setCases(prevCases =>
      prevCases.map(c =>
        c.id === caseId
          ? {
              ...c,
              folders: c.folders.map(folder =>
                folder.id === folderId || folder.name.toLowerCase() === folderId.toLowerCase()
                  ? { ...folder, documents: folder.documents.filter(doc => doc.id !== documentId) }
                  : folder
              ),
            }
          : c
      )
    );

    // If this is the current case, update it as well
    if (currentCase.id === caseId) {
      setCurrentCase(prev => ({
        ...prev,
        folders: prev.folders.map(folder =>
          folder.id === folderId || folder.name.toLowerCase() === folderId.toLowerCase()
            ? { ...folder, documents: folder.documents.filter(doc => doc.id !== documentId) }
            : folder
        ),
      }));

      // S5-007: Sync with backend after a short delay
      setTimeout(() => {
        loadDocumentsFromBackend(caseId);
      }, 500);
    }

    // Clear selected document if it was the deleted one
    if (selectedDocument?.id === documentId) {
      setSelectedDocument(null);
      setViewMode('form');
    }

    console.log(`Document ${documentId} removed from folder ${folderId} in case ${caseId}`);
  };

  // S5-007: Load documents from backend on startup
  const loadDocumentsFromBackend = async (caseId: string) => {
    try {
      console.log(`Loading documents from backend for case: ${caseId}`);

      // Pass current language for localized folder names
      const language = i18n.language || 'de';
      const response = await fetch(`http://localhost:8000/api/documents/tree/${caseId}?language=${language}`);

      if (!response.ok) {
        console.error(`Failed to load documents: ${response.status} ${response.statusText}`);
        return;
      }

      const data = await response.json();
      console.log('Loaded document tree from backend:', data);

      // Transform backend response to frontend Case structure
      setCurrentCase(prev => ({
        ...prev,
        folders: data.folders.map((folder: any) => ({
          id: folder.id,
          name: folder.name,
          nameKey: folder.nameKey,
          localizedName: folder.localizedName,
          documents: folder.documents.map((doc: any) => ({
            id: doc.id,
            name: doc.name,
            type: doc.type,
            size: doc.size,
            uploadedAt: doc.uploadedAt,
            metadata: doc.metadata || {},
            caseId: doc.caseId,
            folderId: doc.folderId,
            renders: doc.renders || [],  // S5-006: Include renders array
          })),
          subfolders: folder.subfolders || [],
          isExpanded: folder.isExpanded !== false,
          mandatory: folder.mandatory || false,
          order: folder.order || 999,
        })),
      }));

      console.log(`Successfully loaded ${data.folders.length} folders from backend`);
    } catch (error) {
      console.error('Error loading documents from backend:', error);
      toast({
        title: 'Failed to load documents',
        description: 'Could not connect to backend. Documents may not be up to date.',
        variant: 'destructive',
      });
    }
  };

  const refreshDocuments = () => {
    // S5-007: Reload documents from backend
    console.log('Refreshing documents for case:', currentCase.id);
    loadDocumentsFromBackend(currentCase.id);
  };

  // WebSocket connection management
  const connectWebSocket = () => {
    // Disconnect existing connection if any
    if (wsConnection) {
      wsConnection.close();
    }

    setWsStatus('connecting');

    try {
      // S5-014: Include language parameter in WebSocket URL
      const wsUrl = `ws://localhost:8000/ws/chat/${currentCase.id}?language=${currentLanguage}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log(`WebSocket connected for case ${currentCase.id}`);
        setWsStatus('connected');
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'chat_response':
              // Non-streaming complete response
              setIsTyping(false);
              addChatMessage({
                role: 'assistant',
                content: message.content,
              });
              break;

            case 'chat_chunk':
              // Streaming response chunk
              if (!message.is_complete) {
                // Stop typing indicator on first chunk
                setIsTyping(false);

                // Accumulate streaming chunks using ref to avoid closure issues
                if (!isStreamingRef.current) {
                  // Create new streaming message
                  isStreamingRef.current = true;
                  const newMessageId = `msg-${Date.now()}`;
                  setStreamingMessageId(newMessageId);
                  addChatMessage({
                    role: 'assistant',
                    content: message.content,
                  });
                } else {
                  // Append to existing streaming message
                  setChatMessages(prev => {
                    const lastMsg = prev[prev.length - 1];
                    if (lastMsg && lastMsg.role === 'assistant') {
                      return [
                        ...prev.slice(0, -1),
                        { ...lastMsg, content: lastMsg.content + message.content }
                      ];
                    }
                    return prev;
                  });
                }
              } else {
                // Streaming complete
                isStreamingRef.current = false;
                setStreamingMessageId(null);
                setIsTyping(false);
              }
              break;

            case 'form_update':
              // Update form fields with extracted values
              Object.entries(message.updates).forEach(([fieldId, value]) => {
                updateFormField(fieldId, value);
              });
              break;

            case 'form_suggestion':
              // S5-002: Handle form suggestions for non-empty fields
              const suggestions = message.suggestions;
              const newSuggestions: FormSuggestions = {};

              Object.entries(suggestions).forEach(([fieldId, suggestion]) => {
                // Only add suggestion if not dismissed
                if (!dismissedSuggestions.has(fieldId)) {
                  newSuggestions[fieldId] = {
                    fieldId,
                    value: suggestion.value,
                    confidence: suggestion.confidence,
                    current: suggestion.current
                  };
                }
              });

              setFormSuggestions(newSuggestions);
              break;

            case 'system':
              addChatMessage({
                role: 'assistant',
                content: message.content,
              });
              break;

            case 'error':
              setIsTyping(false);
              setStreamingMessageId(null);
              addChatMessage({
                role: 'assistant',
                content: `Error: ${message.message}`,
              });
              break;

            case 'anonymization_complete':
              // S5-006: Handle anonymization completion with render support
              setIsAnonymizing(false);
              setIsTyping(false);
              const anonResponse = message as AnonymizationResponse;

              if (anonResponse.success && anonResponse.anonymizedPath) {
                // S5-006: Check if render metadata is present (new render system)
                if (anonResponse.renderMetadata && anonResponse.documentId) {
                  // New behavior: Add render to existing document
                  // Detection data is already included in renderMetadata.metadata from backend
                  const renderData = anonResponse.renderMetadata;

                  setCurrentCase(prev => ({
                    ...prev,
                    folders: prev.folders.map(folder => ({
                      ...folder,
                      documents: folder.documents.map(doc => {
                        if (doc.id === anonResponse.documentId) {
                          // Add the new render to the document
                          const existingRenders = doc.renders || [];
                          return {
                            ...doc,
                            renders: [...existingRenders, renderData],
                          };
                        }
                        return doc;
                      }),
                    })),
                  }));

                  // Update selected document if it's the one that was anonymized
                  if (selectedDocument?.id === anonResponse.documentId) {
                    setSelectedDocument(prev => {
                      if (!prev) return prev;
                      const existingRenders = prev.renders || [];
                      return {
                        ...prev,
                        renders: [...existingRenders, renderData],
                      };
                    });
                  }

                  toast({
                    title: 'Anonymization Complete',
                    description: `Masked ${anonResponse.detectionsCount} PII field${anonResponse.detectionsCount !== 1 ? 's' : ''}. Anonymized render created.`,
                  });

                  // S5-006: Refresh from backend to ensure sync with manifest
                  setTimeout(() => {
                    loadDocumentsFromBackend(currentCase.id);
                  }, 500);
                } else {
                  // Old behavior: Create new document (fallback for backwards compatibility)
                  const pathParts = anonResponse.anonymizedPath.split('/');
                  const anonymizedFileName = pathParts[pathParts.length - 1];
                  const originalFolderId = selectedDocument?.folderId || 'personal-data';
                  const fileExtension = anonymizedFileName.split('.').pop()?.toLowerCase() || 'png';
                  const docType = (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(fileExtension)
                    ? fileExtension
                    : 'png') as Document['type'];

                  const anonymizedDoc: Document = {
                    id: `anon-${Date.now()}`,
                    name: anonymizedFileName,
                    type: docType,
                    size: 'Unknown',
                    uploadedAt: new Date().toISOString(),
                    metadata: { documentType: 'Anonymized Image' },
                    caseId: currentCase.id,
                    folderId: originalFolderId,
                  };

                  setCurrentCase(prev => ({
                    ...prev,
                    folders: prev.folders.map(folder => {
                      if (folder.id === originalFolderId) {
                        const exists = folder.documents.some(doc => doc.name === anonymizedFileName);
                        if (exists) return folder;
                        return {
                          ...folder,
                          documents: [...folder.documents, anonymizedDoc],
                        };
                      }
                      return folder;
                    }),
                  }));

                  setSelectedDocument(anonymizedDoc);

                  toast({
                    title: 'Anonymization Complete',
                    description: `Masked ${anonResponse.detectionsCount} PII field${anonResponse.detectionsCount !== 1 ? 's' : ''}. Document added to folder.`,
                  });
                }
              } else if (anonResponse.error === 'feature_disabled') {
                toast({
                  title: anonResponse.message || i18n.t('anonymization.notImplemented'),
                });
              } else {
                toast({
                  title: 'Anonymization Failed',
                  description: anonResponse.error || 'Unknown error occurred',
                  variant: 'destructive',
                });
              }
              break;

            case 'translation_complete':
              // S5-004/S5-008: Handle translation completion
              setIsTranslating(false);
              setIsTyping(false);
              const translationResponse = message as any;  // TranslationResponse type

              if (translationResponse.success && translationResponse.translatedPath) {
                // S5-006: Check if render metadata is present
                if (translationResponse.renderMetadata && translationResponse.documentId) {
                  // Add render to existing document
                  const renderData = translationResponse.renderMetadata;

                  setCurrentCase(prev => ({
                    ...prev,
                    folders: prev.folders.map(folder => ({
                      ...folder,
                      documents: folder.documents.map(doc => {
                        if (doc.id === translationResponse.documentId) {
                          const existingRenders = doc.renders || [];
                          return {
                            ...doc,
                            renders: [...existingRenders, renderData],
                          };
                        }
                        return doc;
                      }),
                    })),
                  }));

                  // Update selected document if it's the one that was translated
                  if (selectedDocument?.id === translationResponse.documentId) {
                    setSelectedDocument(prev => {
                      if (!prev) return prev;
                      const existingRenders = prev.renders || [];
                      return {
                        ...prev,
                        renders: [...existingRenders, renderData],
                      };
                    });
                  }

                  toast({
                    title: 'Translation Complete',
                    description: `Translated to ${translationResponse.targetLanguage?.toUpperCase()}. Translated render created.`,
                  });

                  // Refresh from backend to ensure sync
                  setTimeout(() => {
                    loadDocumentsFromBackend(currentCase.id);
                  }, 500);
                }
              } else {
                toast({
                  title: 'Translation Failed',
                  description: translationResponse.error || 'Unknown error occurred',
                  variant: 'destructive',
                });
              }
              break;

            default:
              console.warn('Unknown message type:', message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsStatus('error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsStatus('disconnected');
      };

      setWsConnection(ws);
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setWsStatus('error');
    }
  };

  const disconnectWebSocket = () => {
    if (wsConnection) {
      wsConnection.close();
      setWsConnection(null);
      setWsStatus('disconnected');
    }
  };

  const sendChatMessage = (content: string, documentContent?: string) => {
    if (!wsConnection || wsStatus !== 'connected') {
      console.error('WebSocket not connected');
      addChatMessage({
        role: 'assistant',
        content: 'Connection error. Please try reconnecting.',
      });
      return;
    }

    // Reset streaming state for new message
    isStreamingRef.current = false;
    setStreamingMessageId(null);

    // Set typing indicator immediately (before async operations)
    setIsTyping(true);

    // Add user message to chat
    addChatMessage({
      role: 'user',
      content,
    });

    // Check if this is an /anonymize command
    if (content.trim().toLowerCase().startsWith('/anonymize')) {
      // Handle anonymize command - requires a selected image document
      if (!selectedDocument) {
        setIsTyping(false);
        addChatMessage({
          role: 'assistant',
          content: 'Please select an image document first before using /anonymize.',
        });
        return;
      }

      // Check if selected document is an image
      const imageExtensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'];
      const docType = selectedDocument.type?.toLowerCase() || '';
      if (!imageExtensions.includes(docType)) {
        setIsTyping(false);
        addChatMessage({
          role: 'assistant',
          content: `Cannot anonymize "${selectedDocument.name}". Only image files (PNG, JPG, etc.) can be anonymized.`,
        });
        return;
      }

      // Build file path for the selected document
      const filePath = `public/documents/${currentCase.id}/${selectedDocument.folderId}/${selectedDocument.name}`;

      // Send anonymize message type
      // S5-006: Include documentId for render registration
      // S5-014: Include language for localized response messages
      const anonymizeMessage = {
        type: 'anonymize',
        filePath,
        caseId: currentCase.id,
        folderId: selectedDocument.folderId,
        documentId: selectedDocument.id,  // S5-006: Required for render system
        language: currentLanguage,        // S5-014: Include language for response messages
      };

      wsConnection.send(JSON.stringify(anonymizeMessage));
      return;
    }

    // Send regular chat message via WebSocket
    // S5-002: Include current form values for suggestion mode
    const currentFormValues = formFields.reduce((acc, field) => ({
      ...acc,
      [field.id]: field.value
    }), {} as Record<string, string>);

    const message = {
      type: 'chat',
      content,
      caseId: currentCase.id,
      folderId: selectedDocument?.id || null,
      documentContent,
      formSchema: formFields,
      currentFormValues,  // S5-002: For comparison with extracted values
      stream: true,  // Enable streaming by default for performance
      language: currentLanguage,  // S5-014: Include language for AI responses
    };

    wsConnection.send(JSON.stringify(message));
  };

  // S5-003: Perform semantic search
  const performSemanticSearch = async (query: string, documentId: string) => {
    if (!query.trim()) {
      toast({
        title: 'Empty Query',
        description: 'Please enter a search query',
        variant: 'destructive',
      });
      return;
    }

    if (!selectedDocument) {
      toast({
        title: 'No Document Selected',
        description: 'Please select a document to search',
        variant: 'destructive',
      });
      return;
    }

    setIsSearching(true);
    setSearchQuery(query);

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

      // Build request based on document type
      const request: SemanticSearchRequest = {
        query: query.trim(),
        documentType: selectedDocument.type,
        documentContent: selectedDocument.content,
      };

      // For PDFs, provide the document path instead of content
      if (selectedDocument.type === 'pdf') {
        // S5-006: Use selected render's path if applicable
        const activeRender = selectedRender
          ? selectedDocument.renders?.find(r => r.id === selectedRender)
          : null;

        const documentFileName = activeRender
          ? activeRender.filePath.split('/').pop() || selectedDocument.name
          : selectedDocument.name;

        // S5-003: Construct path to PDF - handles both root_docs and case folders
        // Ensure path includes 'public/' prefix for backend filesystem access
        const documentPath = selectedDocument.metadata?.filePath?.includes('root_docs')
          ? `root_docs/${documentFileName}`
          : `public/documents/${currentCase.id}/${selectedDocument.folderId}/${documentFileName}`;

        request.documentPath = documentPath;
        request.documentContent = undefined;
      }

      // Call search API
      const response = await fetch(`${API_BASE_URL}/api/search/semantic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Search failed: ${response.statusText}`);
      }

      const data: SemanticSearchResponse = await response.json();

      // Update highlights
      setSearchHighlights(data.highlights);
      setActiveHighlightIndex(0);

      // Show result toast
      toast({
        title: 'Search Complete',
        description: data.matchSummary,
      });

      console.log(`Search found ${data.count} matches`, data);

    } catch (error) {
      console.error('Search error:', error);

      toast({
        title: 'Search Failed',
        description: error instanceof Error ? error.message : 'An error occurred during search',
        variant: 'destructive',
      });

      // Clear highlights on error
      setSearchHighlights([]);
      setActiveHighlightIndex(0);

    } finally {
      setIsSearching(false);
    }
  };

  // S5-003: Clear search results
  const clearSearch = () => {
    setSearchQuery('');
    setSearchHighlights([]);
    setActiveHighlightIndex(0);
  };

  // S5-003: Clear search when document changes
  useEffect(() => {
    clearSearch();
  }, [selectedDocument?.id]);

  // Clear selectedDocument when case changes (case isolation)
  useEffect(() => {
    // Clear selected document to prevent showing documents from previous case
    setSelectedDocument(null);
    // Reset view mode to form
    setViewMode('form');
  }, [currentCase.id]);

  // S5-007: Load documents from backend when user logs in or case changes
  useEffect(() => {
    if (user && currentCase && currentCase.id) {
      loadDocumentsFromBackend(currentCase.id);
    }
  }, [user, currentCase.id]);

  // Auto-connect when user logs in, case changes, or language changes (S5-014)
  useEffect(() => {
    if (user && currentCase) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [user, currentCase.id, currentLanguage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, []);

  // Persist form fields to localStorage whenever they change
  useEffect(() => {
    const result = saveToLocalStorage('bamf_form_fields', formFields);

    if (!result.success) {
      console.error('Failed to save form fields:', result.error);
      toast({
        title: 'Storage Error',
        description: result.error || 'Failed to save form fields',
        variant: 'destructive',
      });
    } else if (result.warning) {
      console.warn('Storage warning:', result.warning);
      toast({
        title: 'Storage Warning',
        description: result.warning,
        variant: 'default',
      });
    }
  }, [formFields, toast]);

  // Persist case form data to localStorage whenever it changes
  useEffect(() => {
    const result = saveToLocalStorage('bamf_case_form_data', allCaseFormData);

    if (!result.success) {
      console.error('Failed to save case form data:', result.error);
      toast({
        title: 'Storage Error',
        description: result.error || 'Failed to save case form data',
        variant: 'destructive',
      });
    } else if (result.warning) {
      console.warn('Storage warning:', result.warning);
      // Only show warning once to avoid spam
      if (!sessionStorage.getItem('storage_warning_shown')) {
        toast({
          title: 'Storage Warning',
          description: result.warning,
          variant: 'default',
        });
        sessionStorage.setItem('storage_warning_shown', 'true');
      }
    }
  }, [allCaseFormData, toast]);

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
        // S5-006: Render selection
        selectedRender,
        setSelectedRender,
        selectDocumentWithRender,
        // S5-003: Update document content
        updateSelectedDocumentContent,
        formFields,
        setFormFields,
        updateFormField,
        allCaseFormData,
        chatMessages,
        addChatMessage,
        sendChatMessage,
        wsConnection,
        wsStatus,
        connectWebSocket,
        disconnectWebSocket,
        isTyping,
        isAnonymizing,
        setIsAnonymizing,
        isTranslating,
        setIsTranslating,
        addDocumentToFolder,
        removeDocumentFromFolder,
        refreshDocuments,
        highlightedFolder,
        setHighlightedFolder,
        isAdminMode,
        setIsAdminMode,
        isSidebarCollapsed,
        setIsSidebarCollapsed,
        toggleFolder,
        // S5-002: Form suggestions
        formSuggestions,
        acceptSuggestion,
        rejectSuggestion,
        // S5-014: Language toggle
        currentLanguage,
        setLanguage,
        // S5-003: Semantic search
        searchQuery,
        setSearchQuery,
        searchHighlights,
        setSearchHighlights,
        activeHighlightIndex,
        setActiveHighlightIndex,
        isSearching,
        performSemanticSearch,
        clearSearch,
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
