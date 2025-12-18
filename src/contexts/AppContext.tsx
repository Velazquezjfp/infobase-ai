import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Case, Document, FormField, ChatMessage } from '@/types/case';
import { mockCase, initialFormFields, initialChatMessages, sampleCases, sampleCaseFormData, createNewCase } from '@/data/mockData';
import { WebSocketState, ConnectionStatus, WebSocketMessage } from '@/types/websocket';
import { saveToLocalStorage, loadFromLocalStorage } from '@/lib/localStorage';
import { useToast } from '@/hooks/use-toast';

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
  sendChatMessage: (content: string, documentContent?: string) => void;
  // WebSocket
  wsConnection: WebSocket | null;
  wsStatus: ConnectionStatus;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
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
  const { toast } = useToast();

  // Initialize state with localStorage data (with fallback to defaults)
  const [user, setUser] = useState<string | null>(null);
  const [cases, setCases] = useState<Case[]>(sampleCases);
  const [currentCase, setCurrentCase] = useState<Case>(mockCase);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [viewMode, setViewMode] = useState<'document' | 'form' | 'metadata'>('form');

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

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(initialChatMessages);
  const [highlightedFolder, setHighlightedFolder] = useState<string | null>(null);
  const [isAdminMode, setIsAdminMode] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // WebSocket state
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [wsStatus, setWsStatus] = useState<ConnectionStatus>('disconnected');

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

  // WebSocket connection management
  const connectWebSocket = () => {
    // Disconnect existing connection if any
    if (wsConnection) {
      wsConnection.close();
    }

    setWsStatus('connecting');

    try {
      const wsUrl = `ws://localhost:8000/ws/chat/${currentCase.id}`;
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
              addChatMessage({
                role: 'assistant',
                content: message.content,
              });
              break;

            case 'form_update':
              // Update form fields with extracted values
              Object.entries(message.updates).forEach(([fieldId, value]) => {
                updateFormField(fieldId, value);
              });
              break;

            case 'system':
              addChatMessage({
                role: 'assistant',
                content: message.content,
              });
              break;

            case 'error':
              addChatMessage({
                role: 'assistant',
                content: `Error: ${message.message}`,
              });
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

    // Add user message to chat
    addChatMessage({
      role: 'user',
      content,
    });

    // Send message via WebSocket
    const message = {
      type: 'chat',
      content,
      caseId: currentCase.id,
      folderId: selectedDocument?.id || null,
      documentContent,
      formSchema: formFields,
    };

    wsConnection.send(JSON.stringify(message));
  };

  // Clear selectedDocument when case changes (case isolation)
  useEffect(() => {
    // Clear selected document to prevent showing documents from previous case
    setSelectedDocument(null);
    // Reset view mode to form
    setViewMode('form');
  }, [currentCase.id]);

  // Auto-connect when user logs in or case changes
  useEffect(() => {
    if (user && currentCase) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [user, currentCase.id]);

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
