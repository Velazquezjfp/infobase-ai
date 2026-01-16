import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { useApp } from '@/contexts/AppContext';
import {
  ChevronDown,
  ChevronRight,
  Briefcase,
  Folder,
  FileText,
  Scale,
  AlertTriangle,
  CheckCircle,
  Users,
  BookOpen,
  Loader2,
  Bot,
  Layers,
  Settings,
  Plus,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { CustomContextRule } from '@/types/case';

interface ContextNode {
  id: string;
  label: string;
  type: 'case' | 'folder' | 'document' | 'category' | 'item';
  icon: React.ReactNode;
  children?: ContextNode[];
  count?: number;
  isActive?: boolean;
  description?: string;
}

interface ContextHierarchyDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ContextHierarchyDialog({ isOpen, onClose }: ContextHierarchyDialogProps) {
  const { t } = useTranslation();
  const { currentCase, selectedDocument } = useApp();
  const [contextTree, setContextTree] = useState<ContextNode[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['case', 'regulations', 'documents', 'issues', 'custom-rules']));
  const [loading, setLoading] = useState(false);
  const [caseContext, setCaseContext] = useState<any>(null);
  const [customRules, setCustomRules] = useState<CustomContextRule[]>([]);

  // S5-017: Fetch custom rules for the current case
  const fetchCustomRules = useCallback(async () => {
    if (!currentCase) return [];

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/custom-context/${currentCase.id}`);
      if (response.ok) {
        const data = await response.json();
        return data.rules || [];
      }
    } catch (error) {
      console.error('Failed to fetch custom rules:', error);
    }
    return [];
  }, [currentCase]);

  // Fetch case context when dialog opens
  useEffect(() => {
    if (isOpen && currentCase) {
      fetchCaseContext();
    }
  }, [isOpen, currentCase?.id]);

  const fetchCaseContext = async () => {
    setLoading(true);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      // Fetch both case context and custom rules in parallel
      const [contextResponse, rules] = await Promise.all([
        fetch(`${API_BASE_URL}/api/context/case/${currentCase.id}`),
        fetchCustomRules()
      ]);

      setCustomRules(rules);

      if (contextResponse.ok) {
        const data = await contextResponse.json();
        setCaseContext(data);
        buildContextTree(data, rules);
      } else {
        buildContextTree(null, rules);
      }
    } catch (error) {
      console.error('Failed to fetch case context:', error);
      // Build tree with available frontend data
      const rules = await fetchCustomRules();
      setCustomRules(rules);
      buildContextTree(null, rules);
    } finally {
      setLoading(false);
    }
  };

  const buildContextTree = (apiContext: any, rules: CustomContextRule[] = []) => {
    const tree: ContextNode[] = [];

    // Case Level (Akte)
    const caseNode: ContextNode = {
      id: 'case',
      label: `${t('contextHierarchy.case', 'Case')}: ${currentCase.id}`,
      type: 'case',
      icon: <Briefcase className="w-4 h-4 text-primary" />,
      isActive: true,
      description: currentCase.name,
      children: [],
    };

    // Add regulations from API context
    if (apiContext?.regulations?.length > 0) {
      caseNode.children!.push({
        id: 'regulations',
        label: t('contextHierarchy.regulations', 'Articles & Rules'),
        type: 'category',
        icon: <Scale className="w-4 h-4 text-blue-500" />,
        count: apiContext.regulations.length,
        children: apiContext.regulations.slice(0, 5).map((reg: any) => ({
          id: `reg-${reg.id}`,
          label: reg.id,
          type: 'item',
          icon: <BookOpen className="w-3.5 h-3.5 text-muted-foreground" />,
          description: reg.title,
        })),
      });
    }

    // Add required documents from API context
    if (apiContext?.requiredDocuments?.length > 0) {
      // Filter out custom documents (they'll be shown separately)
      const standardDocs = apiContext.requiredDocuments;

      caseNode.children!.push({
        id: 'required-docs',
        label: t('contextHierarchy.requiredDocuments', 'Required Documents'),
        type: 'category',
        icon: <FileText className="w-4 h-4 text-green-500" />,
        count: standardDocs.length,
        children: standardDocs.slice(0, 5).map((doc: any) => ({
          id: `req-${doc.documentType}`,
          label: doc.name,
          type: 'item',
          icon: <FileText className="w-3.5 h-3.5 text-muted-foreground" />,
          description: doc.criticality === 'critical' ? t('contextHierarchy.critical', 'Critical') : t('contextHierarchy.optional', 'Optional'),
        })),
      });
    }

    // Add common issues from API context
    if (apiContext?.commonIssues?.length > 0) {
      caseNode.children!.push({
        id: 'issues',
        label: t('contextHierarchy.commonIssues', 'Common Issues'),
        type: 'category',
        icon: <AlertTriangle className="w-4 h-4 text-warning" />,
        count: apiContext.commonIssues.length,
        children: apiContext.commonIssues.slice(0, 3).map((issue: any, idx: number) => ({
          id: `issue-${idx}`,
          label: issue.issue.substring(0, 40) + (issue.issue.length > 40 ? '...' : ''),
          type: 'item',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-muted-foreground" />,
          description: issue.severity,
        })),
      });
    }

    // Add validation rules from API context
    if (apiContext?.validationRules?.length > 0) {
      caseNode.children!.push({
        id: 'validation',
        label: t('contextHierarchy.validationRules', 'Validation Rules'),
        type: 'category',
        icon: <CheckCircle className="w-4 h-4 text-emerald-500" />,
        count: apiContext.validationRules.length,
        children: apiContext.validationRules.slice(0, 3).map((rule: any) => ({
          id: `rule-${rule.rule_id}`,
          label: rule.rule_id.replace(/_/g, ' '),
          type: 'item',
          icon: <CheckCircle className="w-3.5 h-3.5 text-muted-foreground" />,
        })),
      });
    }

    // S5-017: Add custom rules section (user-added via /Aktenkontext commands)
    if (rules.length > 0) {
      const customValidationRules = rules.filter(r => r.type === 'validation_rule');
      const customDocuments = rules.filter(r => r.type === 'required_document');

      const customChildren: ContextNode[] = [];

      // Custom validation rules
      if (customValidationRules.length > 0) {
        customChildren.push({
          id: 'custom-validation-rules',
          label: t('contextHierarchy.customValidationRules', 'Custom Validation Rules'),
          type: 'category',
          icon: <CheckCircle className="w-4 h-4 text-purple-500" />,
          count: customValidationRules.length,
          children: customValidationRules.map((rule) => ({
            id: rule.id,
            label: rule.rule.length > 40 ? rule.rule.substring(0, 40) + '...' : rule.rule,
            type: 'item',
            icon: <CheckCircle className="w-3.5 h-3.5 text-purple-400" />,
            description: rule.targetFolder ? `${t('contextHierarchy.folder', 'Folder')}: ${rule.targetFolder}` : rule.ruleType || '',
          })),
        });
      }

      // Custom required documents
      if (customDocuments.length > 0) {
        customChildren.push({
          id: 'custom-documents',
          label: t('contextHierarchy.customDocuments', 'Custom Required Documents'),
          type: 'category',
          icon: <Plus className="w-4 h-4 text-purple-500" />,
          count: customDocuments.length,
          children: customDocuments.map((doc) => ({
            id: doc.id,
            label: doc.rule.length > 40 ? doc.rule.substring(0, 40) + '...' : doc.rule,
            type: 'item',
            icon: <FileText className="w-3.5 h-3.5 text-purple-400" />,
            description: doc.targetFolder || '',
          })),
        });
      }

      caseNode.children!.push({
        id: 'custom-rules',
        label: t('contextHierarchy.customRules', 'Custom Rules'),
        type: 'category',
        icon: <Settings className="w-4 h-4 text-purple-500" />,
        count: rules.length,
        children: customChildren,
      });
    }

    tree.push(caseNode);

    // Folder Level - show all folders with their documents
    const foldersNode: ContextNode = {
      id: 'folders',
      label: t('contextHierarchy.folders', 'Folders'),
      type: 'category',
      icon: <Folder className="w-4 h-4 text-yellow-500" />,
      count: currentCase.folders.length,
      children: currentCase.folders.map(folder => {
        const isActiveFolder = selectedDocument?.folderId === folder.id;
        return {
          id: `folder-${folder.id}`,
          label: folder.name,
          type: 'folder' as const,
          icon: <Folder className={cn("w-4 h-4", isActiveFolder ? "text-yellow-500" : "text-muted-foreground")} />,
          isActive: isActiveFolder,
          count: folder.documents.length,
          children: folder.documents.map(doc => ({
            id: `doc-${doc.id}`,
            label: doc.name,
            type: 'document' as const,
            icon: <FileText className={cn("w-3.5 h-3.5", selectedDocument?.id === doc.id ? "text-primary" : "text-muted-foreground")} />,
            isActive: selectedDocument?.id === doc.id,
            description: doc.type.toUpperCase(),
          })),
        };
      }),
    };

    tree.push(foldersNode);

    // Active Document Context (if selected)
    if (selectedDocument) {
      const documentNode: ContextNode = {
        id: 'active-document',
        label: t('contextHierarchy.activeDocument', 'Active Document'),
        type: 'document',
        icon: <FileText className="w-4 h-4 text-primary" />,
        isActive: true,
        description: selectedDocument.name,
        children: [
          {
            id: 'doc-content',
            label: selectedDocument.content
              ? t('contextHierarchy.textExtracted', 'Text content extracted')
              : t('contextHierarchy.noTextContent', 'No text content'),
            type: 'item',
            icon: selectedDocument.content
              ? <CheckCircle className="w-3.5 h-3.5 text-green-500" />
              : <AlertTriangle className="w-3.5 h-3.5 text-muted-foreground" />,
          },
        ],
      };
      tree.push(documentNode);
    }

    setContextTree(tree);
  };

  const toggleNode = (nodeId: string) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  const renderNode = (node: ContextNode, level: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id);

    return (
      <div key={node.id} className="select-none">
        <div
          className={cn(
            "flex items-center gap-2 py-1.5 px-2 rounded-md cursor-pointer transition-colors",
            "hover:bg-accent/50",
            node.isActive && "bg-primary/10 border-l-2 border-primary",
            level > 0 && "ml-4"
          )}
          style={{ marginLeft: level * 16 }}
          onClick={() => hasChildren && toggleNode(node.id)}
        >
          {hasChildren ? (
            <button className="p-0.5 hover:bg-accent rounded">
              {isExpanded ? (
                <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
              )}
            </button>
          ) : (
            <span className="w-4" />
          )}

          {node.icon}

          <span className={cn(
            "text-sm flex-1",
            node.isActive && "font-medium"
          )}>
            {node.label}
          </span>

          {node.count !== undefined && (
            <Badge variant="secondary" className="text-xs px-1.5 py-0">
              {node.count}
            </Badge>
          )}

          {node.description && (
            <span className="text-xs text-muted-foreground truncate max-w-[120px]">
              {node.description}
            </span>
          )}
        </div>

        {hasChildren && isExpanded && (
          <div className="border-l border-border/50 ml-4">
            {node.children!.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl max-h-[80vh] p-0">
        <DialogHeader className="px-6 pt-6 pb-2">
          <DialogTitle className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary" />
            {t('contextHierarchy.title', 'AI Context Hierarchy')}
          </DialogTitle>
          <DialogDescription>
            {t('contextHierarchy.description', 'This shows how context is injected into the AI agent. The hierarchy flows from Case → Folder → Document.')}
          </DialogDescription>
        </DialogHeader>

        {/* Context Flow Indicator */}
        <div className="px-6 py-3 bg-muted/30 border-y border-border">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Bot className="w-4 h-4" />
            <span>{t('contextHierarchy.flowLabel', 'Context Flow')}:</span>
            <div className="flex items-center gap-1">
              <Badge variant="outline" className="text-xs gap-1">
                <Briefcase className="w-3 h-3" />
                {t('contextHierarchy.case', 'Case')}
              </Badge>
              <span>→</span>
              <Badge variant={selectedDocument ? "outline" : "secondary"} className="text-xs gap-1">
                <Folder className="w-3 h-3" />
                {t('contextHierarchy.folder', 'Folder')}
              </Badge>
              <span>→</span>
              <Badge variant={selectedDocument ? "default" : "secondary"} className="text-xs gap-1">
                <FileText className="w-3 h-3" />
                {t('contextHierarchy.document', 'Document')}
              </Badge>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {t('contextHierarchy.precedenceNote', 'Higher specificity takes precedence: Document > Folder > Case')}
          </p>
        </div>

        <ScrollArea className="h-[50vh] px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
              <span className="ml-2 text-muted-foreground">
                {t('contextHierarchy.loading', 'Loading context...')}
              </span>
            </div>
          ) : (
            <div className="space-y-1">
              {contextTree.map(node => renderNode(node))}
            </div>
          )}
        </ScrollArea>

        {/* Footer with source info */}
        <div className="px-6 py-3 bg-muted/30 border-t border-border">
          <p className="text-xs text-muted-foreground">
            {t('contextHierarchy.sourceNote', 'Context data loaded from')}:{' '}
            <code className="bg-muted px-1 rounded text-[10px]">
              backend/data/contexts/cases/{currentCase.id}/
            </code>
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
