import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '@/contexts/AppContext';
import WorkspaceHeader from '@/components/workspace/WorkspaceHeader';
import CaseTreeExplorer from '@/components/workspace/CaseTreeExplorer';
import AIChatInterface from '@/components/workspace/AIChatInterface';
import DocumentViewer from '@/components/workspace/DocumentViewer';
import FormViewer from '@/components/workspace/FormViewer';
import AdminConfigPanel from '@/components/workspace/AdminConfigPanel';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable';

export default function Workspace() {
  const { user, isAdminMode, selectedDocument, setIsSidebarCollapsed } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  // Auto-collapse sidebar when document is selected
  useEffect(() => {
    if (selectedDocument) {
      setIsSidebarCollapsed(true);
    }
  }, [selectedDocument, setIsSidebarCollapsed]);

  if (!user) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      <WorkspaceHeader />
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Collapsible Case Tree */}
        <CaseTreeExplorer />
        
        {/* Resizable panels for Chat, Document, and Form */}
        <ResizablePanelGroup direction="horizontal" className="flex-1">
          {/* Center: AI Chat */}
          <ResizablePanel defaultSize={selectedDocument ? 25 : 40} minSize={15}>
            <AIChatInterface />
          </ResizablePanel>
          
          <ResizableHandle withHandle />
          
          {/* Right side: Document + Form */}
          {selectedDocument ? (
            <>
              <ResizablePanel defaultSize={40} minSize={20}>
                <DocumentViewer />
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={35} minSize={20}>
                <FormViewer />
              </ResizablePanel>
            </>
          ) : (
            <ResizablePanel defaultSize={60} minSize={30}>
              <FormViewer />
            </ResizablePanel>
          )}
        </ResizablePanelGroup>
      </div>
      {isAdminMode && <AdminConfigPanel />}
    </div>
  );
}
