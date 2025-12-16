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

interface NewCaseDialogProps {
  trigger?: React.ReactNode;
}

const caseTemplates = [
  { id: 'integration', name: 'German Integration Course Application' },
  { id: 'asylum', name: 'Asylum Application' },
  { id: 'family', name: 'Family Reunification' },
  { id: 'work', name: 'Work Permit Application' },
  { id: 'custom', name: 'Custom Case' },
];

export default function NewCaseDialog({ trigger }: NewCaseDialogProps) {
  const { addNewCase, switchCase } = useApp();
  const [open, setOpen] = useState(false);
  const [caseName, setCaseName] = useState('');
  const [template, setTemplate] = useState('integration');

  const handleCreate = () => {
    if (!caseName.trim()) {
      toast.error('Please enter a case name');
      return;
    }

    const newCase = addNewCase(caseName.trim());
    switchCase(newCase.id);
    
    toast.success(`Case ${newCase.id} created successfully`);
    
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

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="default" size="sm" className="gap-2">
            <Plus className="w-4 h-4" />
            New Case
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FolderPlus className="w-5 h-5 text-primary" />
            Create New Case
          </DialogTitle>
          <DialogDescription>
            Create a new case with the standard folder structure
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Template Selection */}
          <div className="space-y-2">
            <Label htmlFor="template">Case Template</Label>
            <Select value={template} onValueChange={handleTemplateChange}>
              <SelectTrigger id="template">
                <SelectValue placeholder="Select a template" />
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
            <Label htmlFor="caseName">Case Name</Label>
            <Input
              id="caseName"
              placeholder="Enter case name..."
              value={caseName}
              onChange={(e) => setCaseName(e.target.value)}
            />
          </div>

          {/* Folder Preview */}
          <div className="space-y-2">
            <Label className="text-muted-foreground text-xs">Folders that will be created:</Label>
            <div className="bg-muted/50 rounded-md p-3 space-y-1">
              {['Personal Data', 'Certificates', 'Integration Course Documents', 'Applications & Forms', 'Emails', 'Additional Evidence'].map((folder) => (
                <div key={folder} className="flex items-center gap-2 text-sm">
                  <FileText className="w-3.5 h-3.5 text-primary" />
                  <span>{folder}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreate} disabled={!caseName.trim()}>
            <Plus className="w-4 h-4 mr-2" />
            Create Case
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
