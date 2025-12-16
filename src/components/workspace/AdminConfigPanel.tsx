import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { 
  X, FolderTree, FileType, Zap, FileText, Tags, 
  Plus, Trash2, GripVertical, Save, ChevronDown, ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface FolderTemplate {
  id: string;
  name: string;
  mandatory: boolean;
  children: FolderTemplate[];
}

interface DocumentType {
  id: string;
  name: string;
  mandatory: boolean;
  allowedFormats: string[];
  targetFolder: string;
}

interface MacroConfig {
  id: string;
  name: string;
  trigger: 'upload' | 'manual';
  action: string;
  enabled: boolean;
}

interface MetadataField {
  id: string;
  name: string;
  type: 'text' | 'date' | 'select' | 'number';
  required: boolean;
  options?: string[];
}

export default function AdminConfigPanel() {
  const { setIsAdminMode, formFields, setFormFields } = useApp();
  
  // Folder Templates State
  const [folderTemplates, setFolderTemplates] = useState<FolderTemplate[]>([
    { id: '1', name: 'Personal Data', mandatory: true, children: [] },
    { id: '2', name: 'Certificates', mandatory: true, children: [] },
    { id: '3', name: 'Integration Course Documents', mandatory: true, children: [] },
    { id: '4', name: 'Applications & Forms', mandatory: true, children: [] },
    { id: '5', name: 'Additional Evidence', mandatory: false, children: [] },
  ]);

  // Document Types State
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([
    { id: '1', name: 'Birth Certificate', mandatory: true, allowedFormats: ['pdf', 'jpg', 'png'], targetFolder: 'Personal Data' },
    { id: '2', name: 'Language Certificate', mandatory: true, allowedFormats: ['pdf'], targetFolder: 'Certificates' },
    { id: '3', name: 'Course Completion', mandatory: false, allowedFormats: ['pdf', 'docx'], targetFolder: 'Integration Course Documents' },
    { id: '4', name: 'Application Form', mandatory: true, allowedFormats: ['pdf', 'xml'], targetFolder: 'Applications & Forms' },
  ]);

  // Macros State
  const [macros, setMacros] = useState<MacroConfig[]>([
    { id: '1', name: 'Convert to PDF', trigger: 'upload', action: 'convert_pdf', enabled: true },
    { id: '2', name: 'Translate to German', trigger: 'upload', action: 'translate_de', enabled: true },
    { id: '3', name: 'Extract Metadata', trigger: 'upload', action: 'extract_metadata', enabled: true },
    { id: '4', name: 'Anonymize PII', trigger: 'manual', action: 'anonymize', enabled: false },
  ]);

  // Metadata Fields State
  const [metadataFields, setMetadataFields] = useState<MetadataField[]>([
    { id: '1', name: 'Document Date', type: 'date', required: true },
    { id: '2', name: 'Source', type: 'select', required: true, options: ['Upload', 'Email', 'Scan', 'External System'] },
    { id: '3', name: 'Classification', type: 'select', required: false, options: ['Public', 'Internal', 'Confidential'] },
    { id: '4', name: 'Notes', type: 'text', required: false },
  ]);

  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['1', '2']));

  const toggleFolderExpand = (id: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const addFolder = () => {
    const newFolder: FolderTemplate = {
      id: `folder-${Date.now()}`,
      name: 'New Folder',
      mandatory: false,
      children: [],
    };
    setFolderTemplates([...folderTemplates, newFolder]);
  };

  const removeFolder = (id: string) => {
    setFolderTemplates(folderTemplates.filter(f => f.id !== id));
  };

  const updateFolder = (id: string, updates: Partial<FolderTemplate>) => {
    setFolderTemplates(folderTemplates.map(f => 
      f.id === id ? { ...f, ...updates } : f
    ));
  };

  const addDocumentType = () => {
    const newType: DocumentType = {
      id: `doctype-${Date.now()}`,
      name: 'New Document Type',
      mandatory: false,
      allowedFormats: ['pdf'],
      targetFolder: 'Additional Evidence',
    };
    setDocumentTypes([...documentTypes, newType]);
  };

  const removeDocumentType = (id: string) => {
    setDocumentTypes(documentTypes.filter(d => d.id !== id));
  };

  const updateDocumentType = (id: string, updates: Partial<DocumentType>) => {
    setDocumentTypes(documentTypes.map(d =>
      d.id === id ? { ...d, ...updates } : d
    ));
  };

  const addMacro = () => {
    const newMacro: MacroConfig = {
      id: `macro-${Date.now()}`,
      name: 'New Macro',
      trigger: 'manual',
      action: 'custom',
      enabled: false,
    };
    setMacros([...macros, newMacro]);
  };

  const removeMacro = (id: string) => {
    setMacros(macros.filter(m => m.id !== id));
  };

  const updateMacro = (id: string, updates: Partial<MacroConfig>) => {
    setMacros(macros.map(m =>
      m.id === id ? { ...m, ...updates } : m
    ));
  };

  const addMetadataField = () => {
    const newField: MetadataField = {
      id: `meta-${Date.now()}`,
      name: 'New Field',
      type: 'text',
      required: false,
    };
    setMetadataFields([...metadataFields, newField]);
  };

  const removeMetadataField = (id: string) => {
    setMetadataFields(metadataFields.filter(f => f.id !== id));
  };

  const updateMetadataField = (id: string, updates: Partial<MetadataField>) => {
    setMetadataFields(metadataFields.map(f =>
      f.id === id ? { ...f, ...updates } : f
    ));
  };

  const addFormField = () => {
    const newField = {
      id: `field-${Date.now()}`,
      label: 'New Field',
      value: '',
      type: 'text' as const,
      required: false,
    };
    setFormFields([...formFields, newField]);
  };

  const removeFormField = (id: string) => {
    setFormFields(formFields.filter(f => f.id !== id));
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-muted/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground">Admin Configuration</h2>
              <p className="text-sm text-muted-foreground">Configure templates, document types, and automation</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setIsAdminMode(false)}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          <Tabs defaultValue="folders" className="w-full">
            <TabsList className="grid w-full grid-cols-5 mb-4">
              <TabsTrigger value="folders" className="text-xs sm:text-sm">
                <FolderTree className="w-4 h-4 mr-1.5 hidden sm:inline" />
                Folders
              </TabsTrigger>
              <TabsTrigger value="doctypes" className="text-xs sm:text-sm">
                <FileType className="w-4 h-4 mr-1.5 hidden sm:inline" />
                Doc Types
              </TabsTrigger>
              <TabsTrigger value="macros" className="text-xs sm:text-sm">
                <Zap className="w-4 h-4 mr-1.5 hidden sm:inline" />
                Macros
              </TabsTrigger>
              <TabsTrigger value="forms" className="text-xs sm:text-sm">
                <FileText className="w-4 h-4 mr-1.5 hidden sm:inline" />
                Forms
              </TabsTrigger>
              <TabsTrigger value="metadata" className="text-xs sm:text-sm">
                <Tags className="w-4 h-4 mr-1.5 hidden sm:inline" />
                Metadata
              </TabsTrigger>
            </TabsList>

            {/* Folder Templates Tab */}
            <TabsContent value="folders" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Folder Template Structure</CardTitle>
                  <CardDescription>Define the folder hierarchy for new cases</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {folderTemplates.map((folder) => (
                    <div
                      key={folder.id}
                      className="flex items-center gap-2 p-2 rounded-md border border-border bg-background group"
                    >
                      <GripVertical className="w-4 h-4 text-muted-foreground cursor-grab" />
                      <button 
                        onClick={() => toggleFolderExpand(folder.id)}
                        className="p-0.5"
                      >
                        {expandedFolders.has(folder.id) ? (
                          <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-muted-foreground" />
                        )}
                      </button>
                      <FolderTree className="w-4 h-4 text-primary" />
                      <Input
                        value={folder.name}
                        onChange={(e) => updateFolder(folder.id, { name: e.target.value })}
                        className="flex-1 h-8"
                      />
                      <div className="flex items-center gap-2">
                        <Label className="text-xs text-muted-foreground">Required</Label>
                        <Switch
                          checked={folder.mandatory}
                          onCheckedChange={(checked) => updateFolder(folder.id, { mandatory: checked })}
                        />
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeFolder(folder.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addFolder} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Folder
                  </Button>
                </CardContent>
              </Card>

              {/* YAML Preview */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Template Preview (YAML)</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-3 rounded-md text-xs font-mono overflow-auto max-h-40">
{`folders:
${folderTemplates.map(f => `  - name: "${f.name}"
    mandatory: ${f.mandatory}
    children: []`).join('\n')}`}
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Document Types Tab */}
            <TabsContent value="doctypes" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Document Type Definitions</CardTitle>
                  <CardDescription>Configure mandatory document types and their properties</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {documentTypes.map((docType) => (
                    <div
                      key={docType.id}
                      className="p-3 rounded-md border border-border bg-background space-y-3"
                    >
                      <div className="flex items-center gap-2">
                        <FileType className="w-4 h-4 text-primary" />
                        <Input
                          value={docType.name}
                          onChange={(e) => updateDocumentType(docType.id, { name: e.target.value })}
                          className="flex-1 h-8"
                        />
                        <div className="flex items-center gap-2">
                          <Badge variant={docType.mandatory ? "default" : "secondary"}>
                            {docType.mandatory ? 'Required' : 'Optional'}
                          </Badge>
                          <Switch
                            checked={docType.mandatory}
                            onCheckedChange={(checked) => updateDocumentType(docType.id, { mandatory: checked })}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => removeDocumentType(docType.id)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                      <div className="flex gap-4 pl-6">
                        <div className="flex-1">
                          <Label className="text-xs text-muted-foreground">Allowed Formats</Label>
                          <Input
                            value={docType.allowedFormats.join(', ')}
                            onChange={(e) => updateDocumentType(docType.id, { 
                              allowedFormats: e.target.value.split(',').map(s => s.trim())
                            })}
                            placeholder="pdf, jpg, png"
                            className="h-8 mt-1"
                          />
                        </div>
                        <div className="flex-1">
                          <Label className="text-xs text-muted-foreground">Target Folder</Label>
                          <Select
                            value={docType.targetFolder}
                            onValueChange={(value) => updateDocumentType(docType.id, { targetFolder: value })}
                          >
                            <SelectTrigger className="h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {folderTemplates.map(f => (
                                <SelectItem key={f.id} value={f.name}>{f.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addDocumentType} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Document Type
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Macros Tab */}
            <TabsContent value="macros" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Automation Macros</CardTitle>
                  <CardDescription>Configure automatic actions on document upload</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {macros.map((macro) => (
                    <div
                      key={macro.id}
                      className={cn(
                        "p-3 rounded-md border bg-background space-y-3",
                        macro.enabled ? "border-primary/50" : "border-border"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <Zap className={cn("w-4 h-4", macro.enabled ? "text-primary" : "text-muted-foreground")} />
                        <Input
                          value={macro.name}
                          onChange={(e) => updateMacro(macro.id, { name: e.target.value })}
                          className="flex-1 h-8"
                        />
                        <div className="flex items-center gap-2">
                          <Label className="text-xs text-muted-foreground">Enabled</Label>
                          <Switch
                            checked={macro.enabled}
                            onCheckedChange={(checked) => updateMacro(macro.id, { enabled: checked })}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => removeMacro(macro.id)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                      <div className="flex gap-4 pl-6">
                        <div className="w-40">
                          <Label className="text-xs text-muted-foreground">Trigger</Label>
                          <Select
                            value={macro.trigger}
                            onValueChange={(value: 'upload' | 'manual') => updateMacro(macro.id, { trigger: value })}
                          >
                            <SelectTrigger className="h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="upload">On Upload</SelectItem>
                              <SelectItem value="manual">Manual</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex-1">
                          <Label className="text-xs text-muted-foreground">Action</Label>
                          <Select
                            value={macro.action}
                            onValueChange={(value) => updateMacro(macro.id, { action: value })}
                          >
                            <SelectTrigger className="h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="convert_pdf">Convert to PDF</SelectItem>
                              <SelectItem value="translate_de">Translate to German</SelectItem>
                              <SelectItem value="extract_metadata">Extract Metadata</SelectItem>
                              <SelectItem value="anonymize">Anonymize PII</SelectItem>
                              <SelectItem value="ocr">Run OCR</SelectItem>
                              <SelectItem value="validate">Validate Document</SelectItem>
                              <SelectItem value="custom">Custom Script</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addMacro} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Macro
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Form Definitions Tab */}
            <TabsContent value="forms" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Form Field Definitions</CardTitle>
                  <CardDescription>Configure the form fields for case applications</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {formFields.map((field) => (
                    <div
                      key={field.id}
                      className="flex items-center gap-2 p-2 rounded-md border border-border bg-background group"
                    >
                      <GripVertical className="w-4 h-4 text-muted-foreground cursor-grab" />
                      <Input
                        value={field.label}
                        onChange={(e) => {
                          setFormFields(formFields.map(f => 
                            f.id === field.id ? { ...f, label: e.target.value } : f
                          ));
                        }}
                        className="flex-1 h-8"
                      />
                      <Select
                        value={field.type}
                        onValueChange={(value: 'text' | 'textarea' | 'select' | 'date') => {
                          setFormFields(formFields.map(f =>
                            f.id === field.id ? { ...f, type: value } : f
                          ));
                        }}
                      >
                        <SelectTrigger className="w-28 h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="text">Text</SelectItem>
                          <SelectItem value="textarea">Textarea</SelectItem>
                          <SelectItem value="select">Select</SelectItem>
                          <SelectItem value="date">Date</SelectItem>
                        </SelectContent>
                      </Select>
                      <div className="flex items-center gap-2">
                        <Label className="text-xs text-muted-foreground">Required</Label>
                        <Switch
                          checked={field.required}
                          onCheckedChange={(checked) => {
                            setFormFields(formFields.map(f =>
                              f.id === field.id ? { ...f, required: checked } : f
                            ));
                          }}
                        />
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeFormField(field.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addFormField} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Field
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Metadata Fields Tab */}
            <TabsContent value="metadata" className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Metadata Field Definitions</CardTitle>
                  <CardDescription>Configure custom metadata fields for documents</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {metadataFields.map((field) => (
                    <div
                      key={field.id}
                      className="p-3 rounded-md border border-border bg-background space-y-3"
                    >
                      <div className="flex items-center gap-2">
                        <Tags className="w-4 h-4 text-primary" />
                        <Input
                          value={field.name}
                          onChange={(e) => updateMetadataField(field.id, { name: e.target.value })}
                          className="flex-1 h-8"
                        />
                        <Select
                          value={field.type}
                          onValueChange={(value: 'text' | 'date' | 'select' | 'number') => 
                            updateMetadataField(field.id, { type: value })
                          }
                        >
                          <SelectTrigger className="w-28 h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">Text</SelectItem>
                            <SelectItem value="date">Date</SelectItem>
                            <SelectItem value="select">Select</SelectItem>
                            <SelectItem value="number">Number</SelectItem>
                          </SelectContent>
                        </Select>
                        <div className="flex items-center gap-2">
                          <Label className="text-xs text-muted-foreground">Required</Label>
                          <Switch
                            checked={field.required}
                            onCheckedChange={(checked) => updateMetadataField(field.id, { required: checked })}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => removeMetadataField(field.id)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                      {field.type === 'select' && (
                        <div className="pl-6">
                          <Label className="text-xs text-muted-foreground">Options (comma-separated)</Label>
                          <Input
                            value={field.options?.join(', ') || ''}
                            onChange={(e) => updateMetadataField(field.id, {
                              options: e.target.value.split(',').map(s => s.trim())
                            })}
                            placeholder="Option 1, Option 2, Option 3"
                            className="h-8 mt-1"
                          />
                        </div>
                      )}
                    </div>
                  ))}
                  <Button variant="outline" size="sm" onClick={addMetadataField} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Metadata Field
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-border bg-muted/30">
          <p className="text-xs text-muted-foreground">
            Changes are applied immediately to the current case template
          </p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsAdminMode(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsAdminMode(false)}>
              <Save className="w-4 h-4 mr-2" />
              Save & Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
