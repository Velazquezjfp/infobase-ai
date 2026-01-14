/**
 * S5-008: EmailViewer Component
 *
 * Displays parsed email content with proper formatting for Arabic, German, and English text.
 * Shows email headers (From, To, Subject, Date) and body content with RTL support.
 */

import { Mail, User, Calendar, Paperclip } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useTranslation } from 'react-i18next';

interface EmailAttachment {
  filename: string;
  content_type: string;
  size?: number;
}

interface EmailData {
  from_addr: string;
  to_addr: string;
  subject: string;
  date: string;
  body_text: string;
  body_html?: string | null;
  attachments: EmailAttachment[];
}

interface EmailViewerProps {
  emailData: EmailData;
}

/**
 * Format file size in human-readable format
 */
function formatSize(bytes: number | undefined): string {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Detect if text is primarily RTL (Arabic, Hebrew, etc.)
 */
function isRTLText(text: string): boolean {
  // Check for Arabic Unicode range
  const arabicRegex = /[\u0600-\u06FF]/;
  const hebrewRegex = /[\u0590-\u05FF]/;
  return arabicRegex.test(text) || hebrewRegex.test(text);
}

export default function EmailViewer({ emailData }: EmailViewerProps) {
  const { t } = useTranslation();

  // Detect if email body is RTL
  const isRTL = isRTLText(emailData.body_text);

  return (
    <div className="email-viewer w-full h-full overflow-auto p-4">
      <Card className="max-w-4xl mx-auto">
        <CardHeader className="space-y-3">
          {/* Email Subject */}
          <div className="flex items-start gap-2">
            <Mail className="w-5 h-5 mt-1 text-muted-foreground" />
            <div className="flex-1">
              <h2 className="text-xl font-semibold">
                {emailData.subject || t('email.noSubject', 'No Subject')}
              </h2>
            </div>
          </div>

          <Separator />

          {/* Email Metadata */}
          <div className="space-y-2 text-sm">
            {/* From */}
            <div className="flex items-start gap-2">
              <User className="w-4 h-4 mt-0.5 text-muted-foreground" />
              <div className="flex-1">
                <span className="font-medium text-muted-foreground">
                  {t('email.from', 'From')}:{' '}
                </span>
                <span>{emailData.from_addr}</span>
              </div>
            </div>

            {/* To */}
            <div className="flex items-start gap-2">
              <User className="w-4 h-4 mt-0.5 text-muted-foreground" />
              <div className="flex-1">
                <span className="font-medium text-muted-foreground">
                  {t('email.to', 'To')}:{' '}
                </span>
                <span>{emailData.to_addr}</span>
              </div>
            </div>

            {/* Date */}
            <div className="flex items-start gap-2">
              <Calendar className="w-4 h-4 mt-0.5 text-muted-foreground" />
              <div className="flex-1">
                <span className="font-medium text-muted-foreground">
                  {t('email.date', 'Date')}:{' '}
                </span>
                <span>{emailData.date}</span>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <Separator />

          {/* Email Body */}
          <div
            className={`email-body whitespace-pre-wrap text-sm leading-relaxed ${
              isRTL ? 'text-right' : 'text-left'
            }`}
            dir={isRTL ? 'rtl' : 'ltr'}
            style={{
              fontFamily: isRTL
                ? 'Arial, "Traditional Arabic", "Simplified Arabic", sans-serif'
                : 'inherit',
              lineHeight: '1.8',
            }}
          >
            {emailData.body_text}
          </div>

          {/* Attachments */}
          {emailData.attachments && emailData.attachments.length > 0 && (
            <>
              <Separator />
              <div className="attachments space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <Paperclip className="w-4 h-4" />
                  <span>
                    {t('email.attachments', 'Attachments')} ({emailData.attachments.length})
                  </span>
                </div>
                <ul className="space-y-1 ml-6">
                  {emailData.attachments.map((att, index) => (
                    <li key={index} className="text-sm text-muted-foreground">
                      <span className="font-medium">{att.filename}</span>
                      {att.size && (
                        <span className="text-xs ml-2">({formatSize(att.size)})</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
