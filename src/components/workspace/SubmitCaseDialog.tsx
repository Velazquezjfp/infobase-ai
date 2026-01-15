import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useApp } from '@/contexts/AppContext';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import {
  Loader2,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Info,
  ChevronDown,
  ChevronRight,
  Send,
  Shield,
} from 'lucide-react';

interface ValidationWarning {
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  title: string;
  details: string[];
}

interface ValidationResponse {
  success: boolean;
  score: number;
  summary: string;
  warnings: ValidationWarning[];
  recommendations: string[];
  error?: string;
}

interface SubmitCaseDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: () => void;
}

type DialogState = 'initial' | 'loading' | 'results' | 'error';

const severityConfig = {
  critical: {
    icon: AlertCircle,
    color: 'text-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    label: 'criticalIssues',
  },
  high: {
    icon: AlertTriangle,
    color: 'text-orange-600',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    label: 'highPriority',
  },
  medium: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    label: 'mediumPriority',
  },
  low: {
    icon: Info,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    label: 'lowPriority',
  },
};

function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 50) return 'text-orange-600';
  return 'text-red-600';
}

function getScoreBarColor(score: number): string {
  if (score >= 90) return 'bg-green-500';
  if (score >= 70) return 'bg-yellow-500';
  if (score >= 50) return 'bg-orange-500';
  return 'bg-red-500';
}

function getScoreLabel(score: number, t: (key: string) => string): string {
  if (score >= 90) return t('submitCase.scoreExcellent') || 'Excellent';
  if (score >= 70) return t('submitCase.scoreGood') || 'Good';
  if (score >= 50) return t('submitCase.scoreFair') || 'Fair';
  return t('submitCase.scorePoor') || 'Poor';
}

export default function SubmitCaseDialog({
  open,
  onOpenChange,
  onSubmit,
}: SubmitCaseDialogProps) {
  const { t, i18n } = useTranslation();
  const { currentCase, formFields } = useApp();

  const [dialogState, setDialogState] = useState<DialogState>('initial');
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null);
  const [expandedSeverities, setExpandedSeverities] = useState<Set<string>>(new Set(['critical', 'high']));

  const toggleSeverity = (severity: string) => {
    setExpandedSeverities((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(severity)) {
        newSet.delete(severity);
      } else {
        newSet.add(severity);
      }
      return newSet;
    });
  };

  const handleRunValidation = async () => {
    if (!currentCase) {
      toast({
        title: t('submitCase.validationFailed') || 'Validation Failed',
        description: 'No case selected',
        variant: 'destructive',
      });
      return;
    }

    setDialogState('loading');

    try {
      // Build form data from formFields
      const formData: Record<string, string> = {};
      if (formFields) {
        formFields.forEach((field) => {
          formData[field.id] = field.value || '';
        });
      }

      // Collect cached document contents (text from PDFs) from folders
      const documentContents: Record<string, string> = {};
      if (currentCase?.folders) {
        currentCase.folders.forEach((folder) => {
          folder.documents?.forEach((doc) => {
            if (doc.content) {
              documentContents[doc.id] = doc.content;
            }
          });
        });
      }

      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/validation/case/${currentCase.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          formData,
          language: i18n.language,
          documentContents: Object.keys(documentContents).length > 0 ? documentContents : null,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Validation request failed');
      }

      const result: ValidationResponse = await response.json();
      setValidationResult(result);

      if (result.success) {
        setDialogState('results');
      } else {
        setDialogState('error');
      }
    } catch (error: any) {
      console.error('Validation error:', error);
      setValidationResult({
        success: false,
        score: 0,
        summary: '',
        warnings: [],
        recommendations: [],
        error: error.message || 'Validation failed',
      });
      setDialogState('error');
    }
  };

  const handleSubmitWithoutCheck = () => {
    onSubmit();
    onOpenChange(false);
    resetDialog();
  };

  const handleSubmitAnyway = () => {
    onSubmit();
    onOpenChange(false);
    resetDialog();
  };

  const handleClose = () => {
    onOpenChange(false);
    resetDialog();
  };

  const resetDialog = () => {
    setDialogState('initial');
    setValidationResult(null);
    setExpandedSeverities(new Set(['critical', 'high']));
  };

  // Group warnings by severity
  const groupedWarnings = validationResult?.warnings.reduce(
    (acc, warning) => {
      if (!acc[warning.severity]) {
        acc[warning.severity] = [];
      }
      acc[warning.severity].push(warning);
      return acc;
    },
    {} as Record<string, ValidationWarning[]>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Send className="w-5 h-5" />
            {t('submitCase.title') || 'Submit Case'}
          </DialogTitle>
          {dialogState === 'initial' && (
            <DialogDescription>
              {t('submitCase.confirmMessage') || 'You are about to submit this case.'}
            </DialogDescription>
          )}
        </DialogHeader>

        <div className="flex-1 overflow-y-auto py-4">
          {/* Initial State */}
          {dialogState === 'initial' && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <Shield className="w-8 h-8 text-blue-600 flex-shrink-0" />
                <div>
                  <p className="font-medium text-blue-900">
                    {t('submitCase.askValidation') || 'Would you like to run a validation check first?'}
                  </p>
                  <p className="text-sm text-blue-700 mt-1">
                    {t('submitCase.validationDescription') ||
                      'AI-powered validation will analyze your form data and documents for completeness.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {dialogState === 'loading' && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
              <p className="text-lg font-medium">
                {t('submitCase.validating') || 'Validating case...'}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                {t('submitCase.validatingDescription') ||
                  'Analyzing form data and documents'}
              </p>
            </div>
          )}

          {/* Results State */}
          {dialogState === 'results' && validationResult && (
            <div className="space-y-4">
              {/* Score Display */}
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{t('submitCase.score') || 'Score'}</span>
                  <span className={cn('text-2xl font-bold', getScoreColor(validationResult.score))}>
                    {validationResult.score}/100
                  </span>
                </div>
                <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={cn('h-full transition-all', getScoreBarColor(validationResult.score))}
                    style={{ width: `${validationResult.score}%` }}
                  />
                </div>
                <p className={cn('text-sm mt-1 text-right', getScoreColor(validationResult.score))}>
                  {getScoreLabel(validationResult.score, t)}
                </p>
              </div>

              {/* Summary */}
              <div>
                <h4 className="font-medium mb-2">{t('submitCase.summary') || 'Summary'}</h4>
                <p className="text-sm text-muted-foreground">{validationResult.summary}</p>
              </div>

              {/* Warnings by Severity */}
              {groupedWarnings && Object.keys(groupedWarnings).length > 0 && (
                <div className="space-y-2">
                  {(['critical', 'high', 'medium', 'low'] as const).map((severity) => {
                    const warnings = groupedWarnings[severity];
                    if (!warnings || warnings.length === 0) return null;

                    const config = severityConfig[severity];
                    const Icon = config.icon;
                    const isExpanded = expandedSeverities.has(severity);

                    return (
                      <div
                        key={severity}
                        className={cn('rounded-lg border', config.border, config.bg)}
                      >
                        <button
                          onClick={() => toggleSeverity(severity)}
                          className="w-full p-3 flex items-center justify-between text-left"
                        >
                          <div className="flex items-center gap-2">
                            <Icon className={cn('w-5 h-5', config.color)} />
                            <span className={cn('font-medium', config.color)}>
                              {t(`submitCase.${config.label}`) || config.label} ({warnings.length})
                            </span>
                          </div>
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-muted-foreground" />
                          )}
                        </button>
                        {isExpanded && (
                          <div className="px-3 pb-3 space-y-2">
                            {warnings.map((warning, idx) => (
                              <div
                                key={idx}
                                className="bg-white/50 rounded p-2 border border-white/80"
                              >
                                <p className="font-medium text-sm">{warning.title}</p>
                                {warning.details.length > 0 && (
                                  <ul className="mt-1 text-xs text-muted-foreground list-disc list-inside">
                                    {warning.details.map((detail, dIdx) => (
                                      <li key={dIdx}>{detail}</li>
                                    ))}
                                  </ul>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Recommendations */}
              {validationResult.recommendations.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">
                    {t('submitCase.recommendations') || 'Recommendations'}
                  </h4>
                  <ul className="space-y-1">
                    {validationResult.recommendations.map((rec, idx) => (
                      <li
                        key={idx}
                        className="flex items-start gap-2 text-sm text-muted-foreground"
                      >
                        <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Error State */}
          {dialogState === 'error' && (
            <div className="flex flex-col items-center justify-center py-8">
              <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
              <p className="text-lg font-medium text-red-600">
                {t('submitCase.validationFailed') || 'Validation Failed'}
              </p>
              <p className="text-sm text-muted-foreground mt-1 text-center">
                {validationResult?.error || 'An error occurred during validation'}
              </p>
            </div>
          )}
        </div>

        <DialogFooter className="flex-shrink-0">
          {dialogState === 'initial' && (
            <>
              <Button variant="outline" onClick={handleSubmitWithoutCheck}>
                {t('submitCase.submitWithoutCheck') || 'Submit Without Check'}
              </Button>
              <Button onClick={handleRunValidation}>
                <Shield className="w-4 h-4 mr-2" />
                {t('submitCase.runValidation') || 'Run Validation'}
              </Button>
            </>
          )}

          {dialogState === 'loading' && (
            <Button variant="outline" onClick={handleClose} disabled>
              {t('common.cancel') || 'Cancel'}
            </Button>
          )}

          {dialogState === 'results' && (
            <>
              <Button variant="outline" onClick={handleClose}>
                {t('submitCase.closeAndContinue') || 'Close & Continue Working'}
              </Button>
              <Button onClick={handleSubmitAnyway}>
                <Send className="w-4 h-4 mr-2" />
                {t('submitCase.submitAnyway') || 'Submit Anyway'}
              </Button>
            </>
          )}

          {dialogState === 'error' && (
            <>
              <Button variant="outline" onClick={handleClose}>
                {t('common.close') || 'Close'}
              </Button>
              <Button onClick={handleRunValidation}>
                {t('common.tryAgain') || 'Try Again'}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
