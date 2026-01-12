import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { Plus, FolderPlus, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { useTranslation } from 'react-i18next';

interface NewCaseDialogProps {
  trigger?: React.ReactNode;
}

const caseTemplateIds = ['integration', 'asylum', 'family', 'work', 'custom'] as const;

export default function NewCaseDialog({ trigger }: NewCaseDialogProps) {
  const { addNewCase, switchCase } = useApp();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [caseName, setCaseName] = useState('');
  const [template, setTemplate] = useState('integration');

  const caseTemplates = caseTemplateIds.map(id => ({
    id,
    name: t(`caseTemplates.${id}`)
  }));

  const handleCreate = () => {
    if (!caseName.trim()) {
      toast.error(t('errors.generic'));
      return;
    }

    const newCase = addNewCase(caseName.trim());
    switchCase(newCase.id);

    toast.success(`${t('case.prefix')} ${newCase.id} ${t('success.created')}`);

    setOpen(false);
    setCaseName('');
    setTemplate('integration');
  };

  const handleTemplateChange = (value: string) => {
    setTemplate(value);
    if (value !== 'custom') {
      const selectedTemplate = caseTemplates.find(t => t.id === value);
      if (selectedTemplate) {
        setCaseName(selectedTemplate.name);
      }
    } else {
      setCaseName('');
    }
  };

  const folderNames = [
    'Personal Data',
    'Certificates',
    'Integration Course Documents',
    'Applications & Forms',
    'Emails',
    'Additional Evidence'
  ];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="default" size="sm" className="gap-2">
            <Plus className="w-4 h-4" />
            {t('case.newCase')}
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FolderPlus className="w-5 h-5 text-primary" />
            {t('caseTemplates.createNewCase')}
          </DialogTitle>
          <DialogDescription>
            {t('caseTemplates.createWithFolders')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Template Selection */}
          <div className="space-y-2">
            <Label htmlFor="template">{t('caseTemplates.caseTemplate')}</Label>
            <Select value={template} onValueChange={handleTemplateChange}>
              <SelectTrigger id="template">
                <SelectValue placeholder={t('caseTemplates.selectTemplate')} />
              </SelectTrigger>
              <SelectContent>
                {caseTemplates.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Case Name */}
          <div className="space-y-2">
            <Label htmlFor="caseName">{t('case.caseName')}</Label>
            <Input
              id="caseName"
              placeholder={`${t('common.add')} ${t('case.caseName').toLowerCase()}...`}
              value={caseName}
              onChange={(e) => setCaseName(e.target.value)}
            />
          </div>

          {/* Folder Preview */}
          <div className="space-y-2">
            <Label className="text-muted-foreground text-xs">{t('caseTemplates.folderPreview')}</Label>
            <div className="bg-muted/50 rounded-md p-3 space-y-1">
              {folderNames.map((folder) => (
                <div key={folder} className="flex items-center gap-2 text-sm">
                  <FileText className="w-3.5 h-3.5 text-primary" />
                  <span>{t(`folders.${folder}`, folder)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            {t('common.cancel')}
          </Button>
          <Button onClick={handleCreate} disabled={!caseName.trim()}>
            <Plus className="w-4 h-4 mr-2" />
            {t('case.createCase')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
