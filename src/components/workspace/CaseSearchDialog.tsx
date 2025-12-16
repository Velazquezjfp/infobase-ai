import { useState, useMemo } from 'react';
import { useApp } from '@/contexts/AppContext';
import { Search, FolderOpen, Calendar, FileText, X, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface CaseSearchDialogProps {
  trigger?: React.ReactNode;
  onCaseSelect?: () => void;
}

export default function CaseSearchDialog({ trigger, onCaseSelect }: CaseSearchDialogProps) {
  const { cases, searchCases, switchCase, currentCase, allCaseFormData } = useApp();
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCases = useMemo(() => {
    return searchCases(searchQuery);
  }, [searchQuery, searchCases]);

  const handleSelectCase = (caseId: string) => {
    switchCase(caseId);
    setOpen(false);
    setSearchQuery('');
    onCaseSelect?.();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'pending': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'completed': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getCaseApplicantName = (caseId: string) => {
    const formData = allCaseFormData[caseId];
    if (formData) {
      const nameField = formData.find(f => f.id === 'name');
      return nameField?.value || 'No applicant name';
    }
    return 'No applicant name';
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm" className="gap-2">
            <Search className="w-4 h-4" />
            Search Cases
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            Search Cases
          </DialogTitle>
          <DialogDescription>
            Search by case ID, name, or applicant information
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by ID, name, country, address..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-9"
              autoFocus
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Results Count */}
          <div className="text-xs text-muted-foreground">
            {filteredCases.length} case{filteredCases.length !== 1 ? 's' : ''} found
          </div>

          {/* Case List */}
          <div className="max-h-80 overflow-auto space-y-2">
            {filteredCases.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="w-10 h-10 mx-auto mb-2 opacity-50" />
                <p>No cases found matching "{searchQuery}"</p>
              </div>
            ) : (
              filteredCases.map((caseItem) => (
                <button
                  key={caseItem.id}
                  onClick={() => handleSelectCase(caseItem.id)}
                  className={cn(
                    "w-full p-3 rounded-lg border text-left transition-all",
                    caseItem.id === currentCase.id
                      ? "bg-primary/10 border-primary/30"
                      : "bg-card border-border hover:bg-accent hover:border-accent"
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <FolderOpen className="w-4 h-4 text-primary flex-shrink-0" />
                        <span className="font-mono text-sm font-medium truncate">
                          {caseItem.id}
                        </span>
                        {caseItem.id === currentCase.id && (
                          <Badge variant="secondary" className="text-xs">Current</Badge>
                        )}
                      </div>
                      <p className="text-sm text-foreground mt-1 truncate">
                        {caseItem.name}
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Applicant: {getCaseApplicantName(caseItem.id)}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <Badge className={cn("text-xs", getStatusColor(caseItem.status))}>
                        {caseItem.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {caseItem.createdAt}
                      </span>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
