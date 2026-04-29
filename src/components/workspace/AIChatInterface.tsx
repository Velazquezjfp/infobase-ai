import { useState, useRef, useEffect, useCallback } from 'react';
import { useApp } from '@/contexts/AppContext';
import { slashCommands, hierarchicalSlashCommands, getFolderArguments } from '@/data/mockData';
import { Send, Plus, Search, Languages, EyeOff, FileOutput, CheckCircle, Mail, Database, Bot, Loader2, FileText, FolderOpen, Briefcase, Info, RotateCcw, Folder, Settings, Trash2, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import { formatChatMessage } from '@/lib/messageFormatter';
import { useTranslation } from 'react-i18next';
import { ContextHierarchyDialog } from './ContextHierarchyDialog';
import type { SlashCommandArgument, CustomContextRule } from '@/types/case';

const quickActionIcons: Record<string, React.ReactNode> = {
  '/convert': <FileOutput className="w-3.5 h-3.5" />,
  '/search': <Search className="w-3.5 h-3.5" />,
  '/translate': <Languages className="w-3.5 h-3.5" />,
  '/anonymize': <EyeOff className="w-3.5 h-3.5" />,
  '/addDocument': <Plus className="w-3.5 h-3.5" />,
  '/extractMetadata': <Database className="w-3.5 h-3.5" />,
  '/validateCase': <CheckCircle className="w-3.5 h-3.5" />,
  '/generateEmail': <Mail className="w-3.5 h-3.5" />,
  '/fillForm': <FileOutput className="w-3.5 h-3.5" />,
  '/Aktenkontext': <Settings className="w-3.5 h-3.5" />,
  '/removeAktenkontext': <Trash2 className="w-3.5 h-3.5" />,
  '/Dokumentsuche': <Search className="w-3.5 h-3.5" />,
  '/Dokumente-abfragen': <FileText className="w-3.5 h-3.5" />,
};

// S5-017: Interface for autocomplete suggestion items
interface AutocompleteSuggestion {
  value: string;
  label: string;
  description: string;
  isCommand?: boolean;
  hasChildren?: boolean;
  requiresInput?: boolean;
  placeholder?: string;
}

// Quick actions config with translation keys
// S5-012: Buttons are dynamically filtered based on selected document type
const allQuickActions = [
  { command: '/fillForm', labelKey: 'chat.fillForm' },
  { command: '/search', labelKey: 'chat.search' },
  { command: '/translate', labelKey: 'chat.translate' },
  { command: '/anonymize', labelKey: 'chat.anonymize' },
];

// S5-012: Image extensions for capability filtering
const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];

// S5-012: Get visible quick actions based on document type
// Images: Hide Translate, Fill Form, and Search
// PDF: Hide Anonymize
// Email: Hide Anonymize
const getVisibleQuickActions = (docType: string | undefined) => {
  if (!docType) {
    // No document selected - show all actions
    return allQuickActions;
  }

  const type = docType.toLowerCase();
  const isImage = IMAGE_EXTENSIONS.includes(type);
  const isPdf = type === 'pdf';
  const isEmail = type === 'eml';

  return allQuickActions.filter(action => {
    if (isImage) {
      // Images: Hide Translate, Fill Form, and Search - only show Anonymize
      return action.command === '/anonymize';
    }
    if (isPdf || isEmail) {
      // PDF and Email: Hide Anonymize
      return action.command !== '/anonymize';
    }
    // Other types: show all
    return true;
  });
};

export default function AIChatInterface() {
  const {
    chatMessages,
    addChatMessage,
    sendChatMessage,
    selectedDocument,
    wsStatus,
    setHighlightedFolder,
    setViewMode,
    isTyping,
    currentCase
  } = useApp();
  const { t, i18n } = useTranslation();
  const [input, setInput] = useState('');
  const [showCommands, setShowCommands] = useState(false);
  const [filteredCommands, setFilteredCommands] = useState(slashCommands);
  const [showContextHierarchy, setShowContextHierarchy] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // S5-017: State for hierarchical command autocomplete
  const [autocompleteSuggestions, setAutocompleteSuggestions] = useState<AutocompleteSuggestion[]>([]);
  const [customRules, setCustomRules] = useState<CustomContextRule[]>([]);
  const [isLoadingRules, setIsLoadingRules] = useState(false);

  // S5-017: Fetch custom rules for the current case
  const fetchCustomRules = useCallback(async () => {
    if (!currentCase) return;

    setIsLoadingRules(true);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/custom-context/${currentCase.id}`);
      if (response.ok) {
        const data = await response.json();
        setCustomRules(data.rules || []);
      }
    } catch (error) {
      console.error('Failed to fetch custom rules:', error);
    } finally {
      setIsLoadingRules(false);
    }
  }, [currentCase]);

  // Fetch custom rules when case changes
  useEffect(() => {
    fetchCustomRules();
  }, [fetchCustomRules]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // S5-017: Parse input and generate hierarchical autocomplete suggestions
  const parseCommandInput = useCallback((inputText: string): AutocompleteSuggestion[] => {
    if (!inputText.startsWith('/')) return [];

    const parts = inputText.split(/\s+/);
    const command = parts[0];

    // Check if it's a hierarchical command
    const hierCmd = hierarchicalSlashCommands.find(c => c.command === command);

    if (!hierCmd) {
      // Fall back to simple command filtering
      const search = inputText.slice(1).toLowerCase();
      return slashCommands
        .filter(cmd =>
          cmd.command.toLowerCase().includes(search) ||
          cmd.label.toLowerCase().includes(search)
        )
        .map(cmd => ({
          value: cmd.command,
          label: cmd.label,
          description: cmd.description,
          isCommand: true,
          hasChildren: hierarchicalSlashCommands.some(h => h.command === cmd.command)
        }));
    }

    // Handle /removeAktenkontext with dynamic rules
    if (command === '/removeAktenkontext') {
      if (customRules.length === 0) {
        return [{
          value: '',
          label: t('contextCommands.noRules', 'No custom rules'),
          description: t('contextCommands.noRulesDescription', 'No custom rules have been added yet'),
          isCommand: false
        }];
      }

      // Filter based on what user has typed
      const search = parts.slice(1).join(' ').toLowerCase();
      return customRules
        .filter(rule => rule.rule.toLowerCase().includes(search) || rule.id.includes(search))
        .map(rule => ({
          value: `/removeAktenkontext "${rule.id}"`,
          label: rule.type === 'validation_rule'
            ? t('contextCommands.validationRule', 'Rule')
            : t('contextCommands.requiredDocument', 'Document'),
          description: rule.rule.length > 50 ? rule.rule.substring(0, 50) + '...' : rule.rule,
          isCommand: false
        }));
    }

    // Handle /Aktenkontext hierarchical arguments
    if (command === '/Aktenkontext') {
      const args = hierCmd.arguments || [];

      // No arguments typed yet - show first level options
      if (parts.length === 1) {
        return args.map(arg => ({
          value: `/Aktenkontext ${arg.value}`,
          label: arg.label,
          description: arg.description,
          hasChildren: !!arg.children && arg.children.length > 0
        }));
      }

      // First argument typed (Regeln or Dokumente)
      const firstArg = parts[1];
      const matchedArg = args.find(a => a.value.toLowerCase() === firstArg.toLowerCase());

      if (!matchedArg) {
        // Partial match - filter first level
        return args
          .filter(a => a.value.toLowerCase().startsWith(firstArg.toLowerCase()))
          .map(arg => ({
            value: `/Aktenkontext ${arg.value}`,
            label: arg.label,
            description: arg.description,
            hasChildren: !!arg.children && arg.children.length > 0
          }));
      }

      // Dokumente - requires input directly
      if (matchedArg.value === 'Dokumente') {
        if (parts.length === 2 && matchedArg.requiresInput) {
          return [{
            value: `/Aktenkontext Dokumente `,
            label: t('contextCommands.enterDescription', 'Enter description'),
            description: matchedArg.placeholder || '"Document requirement description"',
            requiresInput: true
          }];
        }
        return []; // User is typing the description
      }

      // Regeln - show sub-options
      if (matchedArg.value === 'Regeln' && matchedArg.children) {
        // Merge static children with dynamic folder names
        let children = [...matchedArg.children];

        // Find the "Ordner" option and add folder names as its children
        const ordnerIdx = children.findIndex(c => c.value === 'Ordner');
        if (ordnerIdx >= 0 && currentCase) {
          const folderArgs = getFolderArguments(currentCase.folders);
          children[ordnerIdx] = {
            ...children[ordnerIdx],
            children: folderArgs
          };
        }

        if (parts.length === 2) {
          // Show second level options
          return children.map(child => ({
            value: `/Aktenkontext Regeln ${child.value}`,
            label: child.label,
            description: child.description,
            hasChildren: !!child.children && child.children.length > 0,
            requiresInput: child.requiresInput,
            placeholder: child.placeholder
          }));
        }

        // Third level - find matched second level arg
        const secondArg = parts[2];
        const matchedChild = children.find(c => c.value.toLowerCase() === secondArg.toLowerCase());

        if (!matchedChild) {
          // Partial match - filter second level
          return children
            .filter(c => c.value.toLowerCase().startsWith(secondArg.toLowerCase()))
            .map(child => ({
              value: `/Aktenkontext Regeln ${child.value}`,
              label: child.label,
              description: child.description,
              hasChildren: !!child.children && child.children.length > 0
            }));
        }

        // If matched child is Ordner, show folder names
        if (matchedChild.value === 'Ordner' && matchedChild.children && matchedChild.children.length > 0) {
          if (parts.length === 3) {
            return matchedChild.children.map(folder => ({
              value: `/Aktenkontext Regeln Ordner ${folder.value}`,
              label: folder.label,
              description: folder.description,
              requiresInput: folder.requiresInput,
              placeholder: folder.placeholder
            }));
          }

          // Fourth level - folder selected, need rule text
          const folderArg = parts[3];
          const matchedFolder = matchedChild.children.find(f => f.value.toLowerCase() === folderArg.toLowerCase());

          if (!matchedFolder && parts.length === 4) {
            // Partial match folder names
            return matchedChild.children
              .filter(f => f.value.toLowerCase().startsWith(folderArg.toLowerCase()))
              .map(folder => ({
                value: `/Aktenkontext Regeln Ordner ${folder.value}`,
                label: folder.label,
                description: folder.description,
                requiresInput: folder.requiresInput,
                placeholder: folder.placeholder
              }));
          }

          if (matchedFolder?.requiresInput && parts.length === 4) {
            return [{
              value: `/Aktenkontext Regeln Ordner ${matchedFolder.value} `,
              label: t('contextCommands.enterRule', 'Enter rule'),
              description: matchedFolder.placeholder || '"Rule description"',
              requiresInput: true
            }];
          }

          return []; // User is typing the rule
        }

        // Non-Ordner rule types - directly need input
        if (matchedChild.requiresInput && parts.length === 3) {
          return [{
            value: `/Aktenkontext Regeln ${matchedChild.value} `,
            label: t('contextCommands.enterRule', 'Enter rule'),
            description: matchedChild.placeholder || '"Rule description"',
            requiresInput: true
          }];
        }

        return []; // User is typing
      }
    }

    // Handle /Dokumentsuche autocomplete
    if (command === '/Dokumentsuche') {
      if (parts.length === 1) {
        return [{
          value: '/Dokumentsuche ',
          label: t('slashCommands.dokumentsuche', 'Hybrid document search'),
          description: t('documentSearch.searchPlaceholder', 'e.g. referenznummer=AKTE-2024-001 "search query"'),
          requiresInput: true,
          placeholder: t('documentSearch.searchPlaceholder')
        }];
      }
      return []; // User is typing the query
    }

    // Handle /Dokumente-abfragen autocomplete
    if (command === '/Dokumente-abfragen') {
      if (parts.length === 1) {
        return [{
          value: '/Dokumente-abfragen ',
          label: t('slashCommands.dokumenteAbfragen', 'Query documents with RAG'),
          description: t('documentSearch.ragPlaceholder', 'e.g. docId1 docId2 "your question"'),
          requiresInput: true,
          placeholder: t('documentSearch.ragPlaceholder')
        }];
      }
      return []; // User is typing the query
    }

    return [];
  }, [currentCase, customRules, t]);

  useEffect(() => {
    if (input.startsWith('/')) {
      const suggestions = parseCommandInput(input);
      setAutocompleteSuggestions(suggestions);
      setShowCommands(suggestions.length > 0);

      // Also update legacy filtered commands for backward compatibility
      const search = input.slice(1).toLowerCase();
      setFilteredCommands(
        slashCommands.filter(cmd =>
          cmd.command.toLowerCase().includes(search) ||
          cmd.label.toLowerCase().includes(search)
        )
      );
    } else {
      setShowCommands(false);
      setAutocompleteSuggestions([]);
    }
  }, [input, parseCommandInput]);

  // S5-017: Process context modification commands
  const processContextCommand = async (command: string): Promise<boolean> => {
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Helper to add user and AI messages
    const addCommandResponse = (userCmd: string, aiResponse: string) => {
      addChatMessage({ role: 'user', content: userCmd });
      addChatMessage({ role: 'assistant', content: aiResponse });
    };

    // Parse /Aktenkontext Regeln Ordner <folder> "<rule>"
    const regelnOrdnerMatch = command.match(/^\/Aktenkontext\s+Regeln\s+Ordner\s+(\S+)\s+"(.+)"$/i);
    if (regelnOrdnerMatch) {
      const [, folder, rule] = regelnOrdnerMatch;
      try {
        const response = await fetch(`${API_BASE_URL}/api/custom-context/${currentCase.id}/rule`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ targetFolder: folder, ruleType: 'folder_rule', rule })
        });

        if (response.ok) {
          const responseMsg = i18n.language === 'de'
            ? '✅ Validierungsskript erstellt und getestet, Ihre Regel ist aktiv.'
            : '✅ Built and tested validation script, your rule is active.';

          addCommandResponse(command, responseMsg);
          fetchCustomRules(); // Refresh rules
          return true;
        }
      } catch (error) {
        console.error('Failed to add rule:', error);
      }
      return false;
    }

    // Parse /Aktenkontext Regeln <type> "<rule>"
    const regelnMatch = command.match(/^\/Aktenkontext\s+Regeln\s+(\w+)\s+"(.+)"$/i);
    if (regelnMatch) {
      const [, ruleType, rule] = regelnMatch;
      try {
        const response = await fetch(`${API_BASE_URL}/api/custom-context/${currentCase.id}/rule`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ruleType: ruleType.toLowerCase(), rule })
        });

        if (response.ok) {
          const responseMsg = i18n.language === 'de'
            ? '✅ Validierungsskript erstellt und getestet, Ihre Regel ist aktiv.'
            : '✅ Built and tested validation script, your rule is active.';

          addCommandResponse(command, responseMsg);
          fetchCustomRules();
          return true;
        }
      } catch (error) {
        console.error('Failed to add rule:', error);
      }
      return false;
    }

    // Parse /Aktenkontext Dokumente "<description>"
    const dokumenteMatch = command.match(/^\/Aktenkontext\s+Dokumente\s+"(.+)"$/i);
    if (dokumenteMatch) {
      const [, description] = dokumenteMatch;
      try {
        const response = await fetch(`${API_BASE_URL}/api/custom-context/${currentCase.id}/document`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description })
        });

        if (response.ok) {
          const responseMsg = i18n.language === 'de'
            ? '✅ Validierungsskript erstellt und getestet, neues erforderliches Dokument zum Kontext hinzugefügt.'
            : '✅ Built and tested validation script, new document required added to context.';

          addCommandResponse(command, responseMsg);
          fetchCustomRules();
          return true;
        }
      } catch (error) {
        console.error('Failed to add document requirement:', error);
      }
      return false;
    }

    // Parse /removeAktenkontext "<ruleId>"
    const removeMatch = command.match(/^\/removeAktenkontext\s+"(.+)"$/i);
    if (removeMatch) {
      const [, ruleId] = removeMatch;
      try {
        const response = await fetch(`${API_BASE_URL}/api/custom-context/${currentCase.id}/${ruleId}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          const responseMsg = i18n.language === 'de'
            ? '✅ Regel erfolgreich entfernt.'
            : '✅ Rule removed successfully.';

          addCommandResponse(command, responseMsg);
          fetchCustomRules();
          return true;
        }
      } catch (error) {
        console.error('Failed to remove rule:', error);
      }
      return false;
    }

    return false;
  };

  // IDIRS: Process /Dokumentsuche and /Dokumente-abfragen commands
  const [isSearching, setIsSearching] = useState(false);

  const processSearchCommand = async (command: string): Promise<boolean> => {
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Parse /Dokumentsuche [key=value ...] "query"
    const searchMatch = command.match(/^\/Dokumentsuche\s+(.*)/);
    if (searchMatch) {
      const args = searchMatch[1];
      // Extract quoted query
      const queryMatch = args.match(/"([^"]+)"/);
      if (!queryMatch) {
        addChatMessage({ role: 'user', content: command });
        addChatMessage({ role: 'assistant', content: t('documentSearch.searchError') + ': Missing query in quotes.' });
        return true;
      }
      const query = queryMatch[1];

      // Extract key=value filters before the quoted query
      const filterPart = args.substring(0, args.indexOf('"')).trim();
      const entityFilters: Record<string, string> = {};
      if (filterPart) {
        const filterPairs = filterPart.match(/(\w+)=(\S+)/g);
        if (filterPairs) {
          for (const pair of filterPairs) {
            const [key, value] = pair.split('=');
            entityFilters[key] = value;
          }
        }
      }

      addChatMessage({ role: 'user', content: command });
      setIsSearching(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/idirs/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query,
            entity_filters: Object.keys(entityFilters).length > 0 ? entityFilters : undefined,
            top_k: 5,
          }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          const msg = errData.error === 'feature_disabled'
            ? t('documentSearch.notImplemented')
            : `${t('documentSearch.searchError')}: ${errData.detail || response.statusText}`;
          addChatMessage({ role: 'assistant', content: msg });
          return true;
        }

        const data = await response.json();
        const results = data.results || data.hits || [];

        if (results.length === 0) {
          addChatMessage({ role: 'assistant', content: t('documentSearch.noResults') });
          return true;
        }

        // Format as markdown table
        const header = `| ${t('documentSearch.docName')} | ${t('documentSearch.docType')} | ${t('documentSearch.docId')} | ${t('documentSearch.score')} |`;
        const separator = '|---|---|---|---|';
        const rows = results.map((r: any) => {
          const name = r.doc_name || r.document_name || '-';
          const type = r.doc_type || r.document_type || '-';
          const docId = r._id || r.doc_id || r.document_id || '-';
          const score = typeof r.score === 'number' ? r.score.toFixed(3) : '-';
          return `| ${name} | ${type} | \`${docId}\` | ${score} |`;
        });

        const resultMsg = `**${t('documentSearch.resultsFound', { count: results.length })}**\n\n${header}\n${separator}\n${rows.join('\n')}`;
        addChatMessage({ role: 'assistant', content: resultMsg });
      } catch (error) {
        addChatMessage({ role: 'assistant', content: `${t('documentSearch.searchError')}: ${(error as Error).message}` });
      } finally {
        setIsSearching(false);
      }
      return true;
    }

    // Parse /Dokumente-abfragen docId1 [docId2...] "question"
    const ragMatch = command.match(/^\/Dokumente-abfragen\s+(.*)/);
    if (ragMatch) {
      const args = ragMatch[1];
      // Extract quoted question
      const questionMatch = args.match(/"([^"]+)"/);
      if (!questionMatch) {
        addChatMessage({ role: 'user', content: command });
        addChatMessage({ role: 'assistant', content: t('documentSearch.ragError') + ': Missing question in quotes.' });
        return true;
      }
      const question = questionMatch[1];

      // Extract doc IDs (everything before the quoted question)
      const docIdPart = args.substring(0, args.indexOf('"')).trim();
      const docIds = docIdPart.split(/\s+/).filter(Boolean);
      if (docIds.length === 0) {
        addChatMessage({ role: 'user', content: command });
        addChatMessage({ role: 'assistant', content: t('documentSearch.ragError') + ': No document IDs provided.' });
        return true;
      }

      addChatMessage({ role: 'user', content: command });
      setIsSearching(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/idirs/rag`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            doc_ids: docIds,
            question,
            language: i18n.language === 'de' ? 'de' : 'en',
          }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          const msg = errData.error === 'feature_disabled'
            ? t('documentSearch.notImplemented')
            : `${t('documentSearch.ragError')}: ${errData.detail || response.statusText}`;
          addChatMessage({ role: 'assistant', content: msg });
          return true;
        }

        const data = await response.json();
        const confidencePercent = (data.confidence * 100).toFixed(1);
        const confidenceEmoji = data.is_high_confidence ? '🟢' : '🟡';
        const disclaimer = data.is_high_confidence
          ? t('documentSearch.highConfidence')
          : t('documentSearch.lowConfidence');

        const resultMsg = `${data.analysis}\n\n---\n${confidenceEmoji} **${t('documentSearch.confidence')}:** ${confidencePercent}% | ${t('documentSearch.chunks')}: ${data.chunk_count}\n\n_${disclaimer}_`;
        addChatMessage({ role: 'assistant', content: resultMsg });
      } catch (error) {
        addChatMessage({ role: 'assistant', content: `${t('documentSearch.ragError')}: ${(error as Error).message}` });
      } finally {
        setIsSearching(false);
      }
      return true;
    }

    return false;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();

    // S5-017: Check if it's a context modification command
    if (userMessage.startsWith('/Aktenkontext') || userMessage.startsWith('/removeAktenkontext')) {
      const processed = await processContextCommand(userMessage);
      if (processed) {
        setInput('');
        setShowCommands(false);
        return;
      }
      // If not processed, continue to send as regular message
    }

    // IDIRS: Check if it's a document search/RAG command
    if (userMessage.startsWith('/Dokumentsuche') || userMessage.startsWith('/Dokumente-abfragen')) {
      const processed = await processSearchCommand(userMessage);
      if (processed) {
        setInput('');
        setShowCommands(false);
        return;
      }
    }

    // Get document content if a document is selected
    const documentContent = selectedDocument?.content;

    // Send message via WebSocket
    sendChatMessage(userMessage, documentContent);

    setInput('');
    setShowCommands(false);
  };

  const insertCommand = (command: string) => {
    // If command ends with space or has requiresInput, just set it
    if (command.endsWith(' ') || command.includes('"')) {
      setInput(command);
    } else {
      setInput(command + ' ');
    }
    setShowCommands(false);
    inputRef.current?.focus();
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('bg-accent/50');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.currentTarget.classList.remove('bg-accent/50');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('bg-accent/50');
    toast({
      title: "File Drop",
      description: "Document drag-and-drop is not yet implemented.",
    });
  };

  // S5-010: Clear conversation history
  const clearChatHistory = async () => {
    if (!currentCase) {
      toast({
        title: t('chat.clearHistoryError') || "Error",
        description: "No case selected",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch(`/api/chat/clear/${currentCase.id}`, {
        method: 'POST',
      });

      const data = await response.json();

      if (data.success) {
        toast({
          title: t('chat.clearHistorySuccess') || "History Cleared",
          description: data.message || `Cleared ${data.messages_cleared} message(s) from conversation history`,
        });
      } else {
        toast({
          title: t('chat.clearHistoryError') || "Error",
          description: data.message || "Failed to clear conversation history",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error clearing chat history:', error);
      toast({
        title: t('chat.clearHistoryError') || "Error",
        description: "Failed to clear conversation history",
        variant: "destructive",
      });
    }
  };

  // S5-009: Format message with markdown rendering and S2-004 source citation highlighting
  // Fix: Only style slash commands for user messages, and only at start of message
  const formatMessage = (content: string, role: 'user' | 'assistant' | 'system' = 'assistant') => {
    // For user messages, check if it starts with a slash command
    if (role === 'user') {
      const slashCommandMatch = content.match(/^(\/\w+)(\s|$)/);
      if (slashCommandMatch) {
        const command = slashCommandMatch[1];
        const rest = content.slice(command.length);
        return (
          <>
            <span className="slash-command font-mono">{command}</span>
            {rest && formatChatMessage(rest)}
          </>
        );
      }
    }
    // S5-009: Use markdown formatter for proper rendering
    return formatChatMessage(content);
  };

  // S2-004: Get active context sources for display
  // Updated: Always show case context, plus folder and document when selected
  const getActiveContextSources = () => {
    const sources: { type: string; name: string; icon: React.ReactNode }[] = [];

    // Case context is always active
    sources.push({
      type: 'Case',
      name: currentCase.id.replace(/^ACTE-/, `${t('case.prefix')}-`),
      icon: <Briefcase className="w-3 h-3" />
    });

    // Check if document is selected (which implies folder context)
    if (selectedDocument) {
      // Add folder context
      const folder = currentCase.folders.find(f => f.id === selectedDocument.folderId);
      if (folder) {
        sources.push({
          type: 'Folder',
          name: folder.name,
          icon: <Folder className="w-3 h-3" />
        });
      }

      // Add document context
      sources.push({
        type: 'Document',
        name: selectedDocument.name,
        icon: <FileText className="w-3 h-3" />
      });
    }

    return sources;
  };

  const contextSources = getActiveContextSources();

  return (
    <div
      className="h-full w-full flex flex-col bg-background border-l border-pane-border"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="pane-header border-b border-pane-border">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-primary" />
          <span>{t('chat.aiAssistant') || 'AI Assistant'}</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              wsStatus === 'connected' && "bg-green-500",
              wsStatus === 'connecting' && "bg-yellow-500 animate-pulse",
              wsStatus === 'disconnected' && "bg-gray-400",
              wsStatus === 'error' && "bg-red-500"
            )} />
            <span className="text-xs text-muted-foreground">
              {wsStatus === 'connected' && (t('chat.connected') || 'Connected')}
              {wsStatus === 'connecting' && (t('chat.connecting') || 'Connecting...')}
              {wsStatus === 'disconnected' && (t('chat.disconnected') || 'Disconnected')}
              {wsStatus === 'error' && (t('chat.connectionError') || 'Connection Error')}
            </span>
          </div>
          {/* S5-010: Clear History Button */}
          <button
            onClick={clearChatHistory}
            disabled={wsStatus !== 'connected'}
            className={cn(
              "p-1.5 rounded-md transition-colors",
              "hover:bg-accent hover:text-accent-foreground",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "text-muted-foreground"
            )}
            title={t('chat.clearHistory') || 'Clear conversation history'}
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* S2-004: Context Source Indicator - Always visible, clickable info icon */}
      <div className="px-4 py-2 bg-muted/30 border-b border-pane-border flex items-center gap-2">
        <button
          onClick={() => setShowContextHierarchy(true)}
          className={cn(
            "p-1 rounded-md transition-colors",
            "hover:bg-accent hover:text-accent-foreground",
            "text-muted-foreground"
          )}
          title={t('contextHierarchy.viewDetails', 'View context details')}
        >
          <Info className="w-3.5 h-3.5" />
        </button>
        <span className="text-xs text-muted-foreground">{t('chat.contextActive', 'Active context')}:</span>
        <div className="flex flex-wrap gap-1.5 flex-1">
          {contextSources.map((source, idx) => (
            <Badge
              key={idx}
              variant={source.type === 'Document' ? 'default' : 'outline'}
              className="text-xs gap-1 px-2 py-0.5 font-normal"
            >
              {source.icon}
              <span className="truncate max-w-[100px]">{source.name}</span>
            </Badge>
          ))}
        </div>
      </div>

      {/* Context Hierarchy Dialog */}
      <ContextHierarchyDialog
        isOpen={showContextHierarchy}
        onClose={() => setShowContextHierarchy(false)}
      />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {chatMessages.map((message) => (
          <div
            key={message.id}
            className={cn(
              'chat-bubble animate-fade-in',
              message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'
            )}
          >
            {formatMessage(message.content, message.role)}
          </div>
        ))}
        {(isTyping || isSearching) && (
          <div className="chat-bubble chat-bubble-ai flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>{isSearching ? t('documentSearch.searching') : t('chat.typing')}</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions - S5-012: Dynamically filtered based on document type */}
      <div className="px-4 py-2 border-t border-pane-border bg-pane-header/30">
        <div className="flex flex-wrap gap-2">
          {getVisibleQuickActions(selectedDocument?.type).map(({ command, labelKey }) => (
            <button
              key={command}
              onClick={() => insertCommand(command)}
              className="command-button"
            >
              {quickActionIcons[command]}
              <span>{t(labelKey)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* S5-017: Hierarchical Command Autocomplete */}
      {showCommands && autocompleteSuggestions.length > 0 && (
        <div className="mx-4 mb-2 bg-card border border-border rounded-lg shadow-lg overflow-hidden animate-fade-in max-h-64 overflow-y-auto">
          {autocompleteSuggestions.slice(0, 8).map((suggestion, idx) => (
            <button
              key={`${suggestion.value}-${idx}`}
              onClick={() => insertCommand(suggestion.value)}
              className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-accent transition-colors text-left"
            >
              {suggestion.isCommand && quickActionIcons[suggestion.value.split(' ')[0]]}
              {suggestion.requiresInput && (
                <span className="text-primary">
                  <ChevronRight className="w-3.5 h-3.5" />
                </span>
              )}
              <div className="flex flex-col flex-1 min-w-0">
                <span className={cn(
                  "text-sm truncate",
                  suggestion.isCommand ? "slash-command font-mono" : "font-medium"
                )}>
                  {suggestion.isCommand ? suggestion.value : suggestion.label}
                </span>
                {suggestion.description && (
                  <span className="text-xs text-muted-foreground truncate">
                    {suggestion.description}
                  </span>
                )}
              </div>
              {suggestion.hasChildren && (
                <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              )}
              {suggestion.requiresInput && suggestion.placeholder && (
                <span className="text-xs text-muted-foreground italic flex-shrink-0">
                  {suggestion.placeholder}
                </span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-pane-border">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t('chat.placeholder')}
              className="w-full h-11 px-4 pr-12 rounded-lg border border-input bg-card text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-muted-foreground hover:text-primary disabled:opacity-50 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
        <p className="mt-2 text-xs text-muted-foreground text-center">
          Type <span className="slash-command">/</span> to see available commands • Drag files here to upload
        </p>
      </form>
    </div>
  );
}
