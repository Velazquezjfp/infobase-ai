import { useState, useRef, useEffect } from 'react';
import { useApp } from '@/contexts/AppContext';
import { slashCommands } from '@/data/mockData';
import { Send, Plus, Search, Languages, EyeOff, FileOutput, CheckCircle, Mail, Database, Bot, Loader2, FileText, FolderOpen, Briefcase, Info, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import { formatChatMessage } from '@/lib/messageFormatter';
import { useTranslation } from 'react-i18next';

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
};

// Quick actions config with translation keys
const quickActionsConfig = [
  { command: '/fillForm', labelKey: 'chat.fillForm' },
  { command: '/search', labelKey: 'chat.search' },
  { command: '/translate', labelKey: 'chat.translate' },
  { command: '/anonymize', labelKey: 'chat.anonymize' },
  { command: '/validateCase', labelKey: 'chat.validate' },
  { command: '/extractMetadata', labelKey: 'chat.metadata' },
];

export default function AIChatInterface() {
  const {
    chatMessages,
    sendChatMessage,
    selectedDocument,
    wsStatus,
    setHighlightedFolder,
    setViewMode,
    isTyping,
    currentCase
  } = useApp();
  const { t } = useTranslation();
  const [input, setInput] = useState('');
  const [showCommands, setShowCommands] = useState(false);
  const [filteredCommands, setFilteredCommands] = useState(slashCommands);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  useEffect(() => {
    if (input.startsWith('/')) {
      setShowCommands(true);
      const search = input.slice(1).toLowerCase();
      setFilteredCommands(
        slashCommands.filter(cmd =>
          cmd.command.toLowerCase().includes(search) ||
          cmd.label.toLowerCase().includes(search)
        )
      );
    } else {
      setShowCommands(false);
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();

    // Get document content if a document is selected
    const documentContent = selectedDocument?.content;

    // Send message via WebSocket
    sendChatMessage(userMessage, documentContent);

    setInput('');
    setShowCommands(false);
  };

  const insertCommand = (command: string) => {
    setInput(command + ' ');
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
  const formatMessage = (content: string) => {
    // S5-009: Use new markdown formatter for proper rendering
    return formatChatMessage(content);
  };

  // S2-004: Get active context sources for display
  const getActiveContextSources = () => {
    const sources: { type: string; name: string; icon: React.ReactNode }[] = [];

    // Check if document is selected
    if (selectedDocument) {
      sources.push({
        type: 'Document',
        name: selectedDocument.name,
        icon: <FileText className="w-3 h-3" />
      });
    }

    // Note: Folder and Case context would come from AppContext
    // These would be populated when the user is working within a case
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

      {/* S2-004: Context Source Indicator */}
      {contextSources.length > 0 && (
        <div className="px-4 py-2 bg-muted/30 border-b border-pane-border flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">Active context:</span>
          <div className="flex flex-wrap gap-1.5">
            {contextSources.map((source, idx) => (
              <Badge
                key={idx}
                variant="outline"
                className="text-xs gap-1 px-2 py-0.5 font-normal"
              >
                {source.icon}
                <span className="truncate max-w-[100px]">{source.name}</span>
              </Badge>
            ))}
          </div>
        </div>
      )}

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
            {formatMessage(message.content)}
          </div>
        ))}
        {isTyping && (
          <div className="chat-bubble chat-bubble-ai flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>{t('chat.typing')}</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2 border-t border-pane-border bg-pane-header/30">
        <div className="flex flex-wrap gap-2">
          {quickActionsConfig.map(({ command, labelKey }) => (
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

      {/* Command Autocomplete */}
      {showCommands && filteredCommands.length > 0 && (
        <div className="mx-4 mb-2 bg-card border border-border rounded-lg shadow-lg overflow-hidden animate-fade-in">
          {filteredCommands.slice(0, 6).map((cmd) => (
            <button
              key={cmd.command}
              onClick={() => insertCommand(cmd.command)}
              className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-accent transition-colors text-left"
            >
              <span className="slash-command font-mono text-sm">{cmd.command}</span>
              <span className="text-sm text-muted-foreground">{cmd.description}</span>
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
