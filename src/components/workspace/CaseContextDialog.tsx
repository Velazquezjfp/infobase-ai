import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Scale,
  AlertTriangle,
  CheckCircle,
  Folder,
  User,
  BookOpen,
  Loader2,
  ExternalLink,
  Info,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Regulation {
  id: string;
  title: string;
  summary: string;
  url?: string;
}

interface RequiredDocument {
  name: string;
  documentType: string;
  description: string;
  criticality: 'critical' | 'optional';
  acceptedFormats?: string[];
  validationRules?: string[];
  notes?: string;
}

interface ValidationRule {
  rule_id: string;
  condition: string;
  action: string;
}

interface CommonIssue {
  issue: string;
  severity: 'error' | 'warning' | 'info';
  category: string;
  frequency?: string;
  suggestion: string;
}

interface Applicant {
  name: string;
  dateOfBirth: string;
  nationality: string;
  currentStatus: string;
}

interface FolderContext {
  folderId: string;
  folderName: string;
  purpose: string;
  expectedDocuments?: string[];
  validationCriteria?: Array<{
    criterionId: string;
    description: string;
    checkPoints?: string[];
  }>;
}

interface CaseContext {
  schemaVersion: string;
  caseId: string;
  caseType: string;
  name: string;
  description: string;
  applicant?: Applicant;
  regulations: Regulation[];
  requiredDocuments: RequiredDocument[];
  validationRules: ValidationRule[];
  commonIssues: CommonIssue[];
  folders?: FolderContext[];
}

interface CaseContextDialogProps {
  isOpen: boolean;
  onClose: () => void;
  caseId: string;
}

export function CaseContextDialog({ isOpen, onClose, caseId }: CaseContextDialogProps) {
  const { t, i18n } = useTranslation();
  const [context, setContext] = useState<CaseContext | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAllRules, setShowAllRules] = useState(false);

  // Helper to translate content with fallback to original
  const tc = (key: string, fallback: string) => {
    const translated = t(`caseContext.content.${key}`, { defaultValue: '__NOT_FOUND__' });
    return translated === '__NOT_FOUND__' ? fallback : translated;
  };

  useEffect(() => {
    if (isOpen && caseId) {
      fetchCaseContext();
    }
  }, [isOpen, caseId]);

  const fetchCaseContext = async () => {
    setLoading(true);
    setError(null);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/context/case/${caseId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch context: ${response.statusText}`);
      }

      const data = await response.json();
      setContext(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load context');
      console.error('Failed to fetch case context:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'warning':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'info':
        return 'bg-primary/10 text-primary border-primary/20';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getCriticalityBadge = (criticality: string) => {
    if (criticality === 'critical') {
      return <Badge variant="destructive" className="text-xs">{t('caseContext.critical', 'Critical')}</Badge>;
    }
    return <Badge variant="secondary" className="text-xs">{t('caseContext.optional', 'Optional')}</Badge>;
  };

  // Translate case type
  const translateCaseType = (caseType: string) => {
    return tc(`caseTypes.${caseType}`, caseType.replace(/_/g, ' '));
  };

  // Translate case name
  const translateCaseName = (name: string) => {
    return tc(`caseNames.${name.replace(/\s+/g, '_')}`, name);
  };

  // Translate case description
  const translateDescription = (desc: string, caseType: string) => {
    return tc(`descriptions.${caseType}`, desc);
  };

  // Translate applicant status
  const translateStatus = (status: string) => {
    return tc(`statuses.${status.replace(/\s+/g, '_')}`, status);
  };

  // Translate nationality
  const translateNationality = (nationality: string) => {
    return tc(`nationalities.${nationality}`, nationality);
  };

  // Translate validation rule
  const translateValidationRule = (ruleId: string, condition: string) => {
    return tc(`validationRules.${ruleId}`, condition);
  };

  // Translate regulation
  const translateRegulation = (regId: string, field: 'title' | 'summary', fallback: string) => {
    return tc(`regulations.${regId}.${field}`, fallback);
  };

  // Translate document
  const translateDocument = (docType: string, field: 'name' | 'description' | 'notes', fallback: string) => {
    return tc(`documents.${docType}.${field}`, fallback);
  };

  // Translate folder
  const translateFolder = (folderId: string, field: 'name' | 'purpose', fallback: string) => {
    return tc(`folders.${folderId}.${field}`, fallback);
  };

  // Translate expected document type
  const translateDocType = (docType: string) => {
    return tc(`docTypes.${docType}`, docType.replace(/_/g, ' '));
  };

  // Translate validation criterion
  const translateCriterion = (criterionId: string, fallback: string) => {
    return tc(`criteria.${criterionId}`, fallback);
  };

  // Translate common issue
  const translateIssue = (issue: string, field: 'issue' | 'suggestion', fallback: string) => {
    const key = issue.replace(/\s+/g, '_').substring(0, 50);
    return tc(`issues.${key}.${field}`, fallback);
  };

  // Translate checkPoint
  const translateCheckPoint = (checkPoint: string) => {
    const key = checkPoint.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '');
    return tc(`checkPoints.${key}`, checkPoint);
  };

  // Translate category
  const translateCategory = (category: string) => {
    return tc(`categories.${category}`, category.replace(/_/g, ' '));
  };

  // Translate frequency
  const translateFrequency = (frequency: string) => {
    return tc(`frequencies.${frequency}`, frequency.replace(/_/g, ' '));
  };

  // Force re-render when language changes
  const currentLanguage = i18n.language;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[85vh] p-0" key={`context-dialog-${currentLanguage}`}>
        <DialogHeader className="px-6 pt-6 pb-2">
          <DialogTitle className="flex items-center gap-2">
            <Info className="w-5 h-5 text-primary" />
            {t('caseContext.title', 'Case Context')}
          </DialogTitle>
          <DialogDescription>
            {t('caseContext.description', 'AI agent context information for this case. This shows what information is available to the AI assistant.')}
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <span className="ml-2 text-muted-foreground">{t('caseContext.loading', 'Loading context...')}</span>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-12 text-destructive">
            <AlertTriangle className="w-5 h-5 mr-2" />
            {error}
          </div>
        ) : context ? (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
            <div className="px-6 border-b">
              <TabsList className="h-10">
                <TabsTrigger value="overview" className="gap-1.5">
                  <User className="w-4 h-4" />
                  {t('caseContext.tabs.overview', 'Overview')}
                </TabsTrigger>
                <TabsTrigger value="regulations" className="gap-1.5">
                  <Scale className="w-4 h-4" />
                  {t('caseContext.tabs.regulations', 'Regulations')}
                  <Badge variant="secondary" className="ml-1 text-xs">{context.regulations?.length || 0}</Badge>
                </TabsTrigger>
                <TabsTrigger value="documents" className="gap-1.5">
                  <FileText className="w-4 h-4" />
                  {t('caseContext.tabs.documents', 'Documents')}
                  <Badge variant="secondary" className="ml-1 text-xs">{context.requiredDocuments?.length || 0}</Badge>
                </TabsTrigger>
                <TabsTrigger value="folders" className="gap-1.5">
                  <Folder className="w-4 h-4" />
                  {t('caseContext.tabs.folders', 'Folders')}
                  <Badge variant="secondary" className="ml-1 text-xs">{context.folders?.length || 0}</Badge>
                </TabsTrigger>
                <TabsTrigger value="issues" className="gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  {t('caseContext.tabs.issues', 'Common Issues')}
                  <Badge variant="secondary" className="ml-1 text-xs">{context.commonIssues?.length || 0}</Badge>
                </TabsTrigger>
              </TabsList>
            </div>

            <ScrollArea className="h-[55vh] px-6 py-4">
              {/* Overview Tab */}
              <TabsContent value="overview" className="mt-0 space-y-6">
                {/* Case Info */}
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    {t('caseContext.caseInfo', 'Case Information')}
                  </h3>
                  <div className="bg-muted/50 rounded-lg p-4 space-y-2">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs text-muted-foreground">{t('caseContext.caseId', 'Case ID')}</span>
                        <p className="font-medium">{context.caseId}</p>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground">{t('caseContext.caseType', 'Case Type')}</span>
                        <p className="font-medium">{translateCaseType(context.caseType)}</p>
                      </div>
                    </div>
                    <div>
                      <span className="text-xs text-muted-foreground">{t('caseContext.caseName', 'Name')}</span>
                      <p className="font-medium">{translateCaseName(context.name)}</p>
                    </div>
                    <div>
                      <span className="text-xs text-muted-foreground">{t('caseContext.caseDescription', 'Description')}</span>
                      <p className="text-sm text-muted-foreground">{translateDescription(context.description, context.caseType)}</p>
                    </div>
                  </div>
                </div>

                {/* Applicant Info */}
                {context.applicant && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold flex items-center gap-2">
                      <User className="w-4 h-4 text-primary" />
                      {t('caseContext.applicantInfo', 'Applicant Information')}
                    </h3>
                    <div className="bg-muted/50 rounded-lg p-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-xs text-muted-foreground">{t('caseContext.applicantName', 'Name')}</span>
                          <p className="font-medium">{context.applicant.name}</p>
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground">{t('caseContext.dateOfBirth', 'Date of Birth')}</span>
                          <p className="font-medium">{context.applicant.dateOfBirth}</p>
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground">{t('caseContext.nationality', 'Nationality')}</span>
                          <p className="font-medium">{translateNationality(context.applicant.nationality)}</p>
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground">{t('caseContext.currentStatus', 'Current Status')}</span>
                          <p className="font-medium">{translateStatus(context.applicant.currentStatus)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Validation Rules Summary */}
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-primary" />
                    {t('caseContext.validationRules', 'Validation Rules')}
                    <Badge variant="secondary" className="text-xs">{context.validationRules?.length || 0}</Badge>
                  </h3>
                  <div className="space-y-2">
                    {(showAllRules ? context.validationRules : context.validationRules?.slice(0, 5))?.map((rule) => (
                      <div key={rule.rule_id} className="bg-muted/50 rounded-lg p-3">
                        <p className="text-sm font-medium">{tc(`ruleNames.${rule.rule_id}`, rule.rule_id.replace(/_/g, ' '))}</p>
                        <p className="text-xs text-muted-foreground mt-1">{translateValidationRule(rule.rule_id, rule.condition)}</p>
                      </div>
                    ))}
                    {context.validationRules && context.validationRules.length > 5 && (
                      <button
                        onClick={() => setShowAllRules(!showAllRules)}
                        className="w-full text-xs text-primary hover:text-primary/80 text-center py-2 hover:bg-muted/50 rounded transition-colors"
                      >
                        {showAllRules
                          ? t('caseContext.showLess', 'Show less')
                          : `+${context.validationRules.length - 5} ${t('caseContext.moreRules', 'more rules')}`
                        }
                      </button>
                    )}
                  </div>
                </div>
              </TabsContent>

              {/* Regulations Tab */}
              <TabsContent value="regulations" className="mt-0 space-y-3">
                <p className="text-sm text-muted-foreground mb-4">
                  {t('caseContext.regulationsDescription', 'German laws and regulations applicable to this case type.')}
                </p>
                {context.regulations?.map((reg) => (
                  <div key={reg.id} className="border rounded-lg p-4 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <Badge variant="outline" className="mb-2">{reg.id}</Badge>
                        <h4 className="font-medium">{translateRegulation(reg.id, 'title', reg.title)}</h4>
                      </div>
                      {reg.url && (
                        <a
                          href={reg.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline flex items-center gap-1 text-xs"
                        >
                          <ExternalLink className="w-3 h-3" />
                          {t('caseContext.viewLaw', 'View')}
                        </a>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{translateRegulation(reg.id, 'summary', reg.summary)}</p>
                  </div>
                ))}
              </TabsContent>

              {/* Required Documents Tab */}
              <TabsContent value="documents" className="mt-0 space-y-3">
                <p className="text-sm text-muted-foreground mb-4">
                  {t('caseContext.documentsDescription', 'Documents required for this case type with their validation requirements.')}
                </p>
                {context.requiredDocuments?.map((doc, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium flex items-center gap-2">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          {translateDocument(doc.documentType, 'name', doc.name)}
                        </h4>
                        <p className="text-xs text-muted-foreground mt-1">{translateDocType(doc.documentType)}</p>
                      </div>
                      {getCriticalityBadge(doc.criticality)}
                    </div>
                    <p className="text-sm text-muted-foreground">{translateDocument(doc.documentType, 'description', doc.description)}</p>
                    {doc.acceptedFormats && (
                      <div className="flex items-center gap-1 flex-wrap">
                        <span className="text-xs text-muted-foreground">{t('caseContext.formats', 'Formats')}:</span>
                        {doc.acceptedFormats.map((format) => (
                          <Badge key={format} variant="secondary" className="text-xs">{format}</Badge>
                        ))}
                      </div>
                    )}
                    {doc.notes && (
                      <div className="bg-muted/50 rounded p-2 text-xs text-muted-foreground">
                        <Info className="w-3 h-3 inline mr-1" />
                        {translateDocument(doc.documentType, 'notes', doc.notes)}
                      </div>
                    )}
                  </div>
                ))}
              </TabsContent>

              {/* Folders Tab */}
              <TabsContent value="folders" className="mt-0 space-y-3">
                <p className="text-sm text-muted-foreground mb-4">
                  {t('caseContext.foldersDescription', 'Folder structure and their expected contents for this case.')}
                </p>
                {context.folders?.map((folder) => (
                  <div key={folder.folderId} className="border rounded-lg p-4 space-y-2">
                    <div className="flex items-center gap-2">
                      <Folder className="w-4 h-4 text-warning" />
                      <h4 className="font-medium">{translateFolder(folder.folderId, 'name', folder.folderName)}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">{translateFolder(folder.folderId, 'purpose', folder.purpose)}</p>
                    {folder.expectedDocuments && folder.expectedDocuments.length > 0 && (
                      <div>
                        <span className="text-xs font-medium">{t('caseContext.expectedDocs', 'Expected Documents')}:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {folder.expectedDocuments.map((docType) => (
                            <Badge key={docType} variant="outline" className="text-xs">
                              {translateDocType(docType)}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {folder.validationCriteria && folder.validationCriteria.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs font-medium">{t('caseContext.validationCriteria', 'Validation Criteria')}:</span>
                        <ul className="list-disc list-inside mt-1">
                          {folder.validationCriteria.map((criterion) => (
                            <li key={criterion.criterionId} className="text-xs text-muted-foreground">
                              {translateCriterion(criterion.criterionId, criterion.description)}
                              {criterion.checkPoints && criterion.checkPoints.length > 0 && (
                                <ul className="list-disc list-inside ml-4 mt-1">
                                  {criterion.checkPoints.map((cp, idx) => (
                                    <li key={idx} className="text-xs text-muted-foreground/80">
                                      {translateCheckPoint(cp)}
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </TabsContent>

              {/* Common Issues Tab */}
              <TabsContent value="issues" className="mt-0 space-y-3">
                <p className="text-sm text-muted-foreground mb-4">
                  {t('caseContext.issuesDescription', 'Common issues encountered in this case type and recommended solutions.')}
                </p>
                {context.commonIssues?.map((issue, index) => (
                  <div
                    key={index}
                    className={cn(
                      'border rounded-lg p-4 space-y-2',
                      getSeverityColor(issue.severity)
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        {issue.severity === 'error' && <AlertTriangle className="w-4 h-4" />}
                        {issue.severity === 'warning' && <AlertTriangle className="w-4 h-4" />}
                        {issue.severity === 'info' && <Info className="w-4 h-4" />}
                        <span className="font-medium text-sm">{translateIssue(issue.issue, 'issue', issue.issue)}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">{translateCategory(issue.category)}</Badge>
                        {issue.frequency && (
                          <Badge variant="secondary" className="text-xs">{translateFrequency(issue.frequency)}</Badge>
                        )}
                      </div>
                    </div>
                    <div className="bg-background/50 rounded p-2">
                      <span className="text-xs font-medium">{t('caseContext.suggestion', 'Suggestion')}:</span>
                      <p className="text-xs mt-1">{translateIssue(issue.issue, 'suggestion', issue.suggestion)}</p>
                    </div>
                  </div>
                ))}
              </TabsContent>
            </ScrollArea>
          </Tabs>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
