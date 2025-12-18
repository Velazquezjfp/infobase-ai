import { useState, useRef, useEffect } from 'react';
import { useApp } from '@/contexts/AppContext';
import { slashCommands } from '@/data/mockData';
import { Send, Plus, Search, Languages, EyeOff, FileOutput, CheckCircle, Mail, Database, Bot, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from '@/hooks/use-toast';

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

const quickActions = [
  { command: '/fillForm', label: 'Fill Form' },
  { command: '/search', label: 'Search' },
  { command: '/translate', label: 'Translate' },
  { command: '/anonymize', label: 'Anonymize' },
  { command: '/validateCase', label: 'Validate' },
  { command: '/extractMetadata', label: 'Metadata' },
];

export default function AIChatInterface() {
  const {
    chatMessages,
    sendChatMessage,
    selectedDocument,
    wsStatus,
    setHighlightedFolder,
    setViewMode
  } = useApp();
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
    addChatMessage({
      role: 'user',
      content: 'I\'ve uploaded a document. Please analyze it.',
    });
    setTimeout(() => {
      addChatMessage({
        role: 'assistant',
        content: 'I\'ve received the document. Analyzing content...\n\n**Detected document type:** Certificate\n**Suggested folder:** Certificates\n**Extracted information:**\n• Name: Ahmed Ali\n• Issue Date: 2023-06-15\n\nWould you like me to:\n1. Move this to the Certificates folder?\n2. Auto-fill the form with extracted data?',
      });
    }, 1500);
  };

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, i) => {
      // Bold text
      line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      // Checkmarks and warnings
      line = line.replace(/✅/g, '<span class="text-success">✅</span>');
      line = line.replace(/⚠️/g, '<span class="text-warning">⚠️</span>');
      // Slash commands
      line = line.replace(/(\/\w+)/g, '<span class="slash-command">$1</span>');
      return <p key={i} dangerouslySetInnerHTML={{ __html: line || '&nbsp;' }} />;
    });
  };

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
          <span>AI Assistant</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            wsStatus === 'connected' && "bg-green-500",
            wsStatus === 'connecting' && "bg-yellow-500 animate-pulse",
            wsStatus === 'disconnected' && "bg-gray-400",
            wsStatus === 'error' && "bg-red-500"
          )} />
          <span className="text-xs text-muted-foreground">
            {wsStatus === 'connected' && 'Connected'}
            {wsStatus === 'connecting' && 'Connecting...'}
            {wsStatus === 'disconnected' && 'Disconnected'}
            {wsStatus === 'error' && 'Connection Error'}
          </span>
        </div>
      </div>

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
            <span>Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2 border-t border-pane-border bg-pane-header/30">
        <div className="flex flex-wrap gap-2">
          {quickActions.map(({ command, label }) => (
            <button
              key={command}
              onClick={() => insertCommand(command)}
              className="command-button"
            >
              {quickActionIcons[command]}
              <span>{label}</span>
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
              placeholder="Type a message or / for commands..."
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
