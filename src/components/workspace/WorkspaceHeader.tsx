import { useApp } from '@/contexts/AppContext';
import { Shield, LogOut, Settings, User, ToggleLeft, ToggleRight, Search, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import CaseSearchDialog from './CaseSearchDialog';
import NewCaseDialog from './NewCaseDialog';

export default function WorkspaceHeader() {
  const { user, setUser, isAdminMode, setIsAdminMode, currentCase } = useApp();
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    navigate('/');
  };

  return (
    <header className="h-14 px-4 border-b border-pane-border bg-card flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="font-semibold text-foreground">BAMF</span>
        </div>
        <div className="h-6 w-px bg-border" />
        <div>
          <p className="text-sm font-medium text-foreground">{currentCase.name}</p>
          <p className="text-xs text-muted-foreground">{currentCase.id}</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Case Actions */}
        <div className="flex items-center gap-2">
          <CaseSearchDialog
            trigger={
              <Button variant="outline" size="sm" className="gap-2">
                <Search className="w-4 h-4" />
                <span className="hidden sm:inline">Search</span>
              </Button>
            }
          />
          <NewCaseDialog
            trigger={
              <Button variant="default" size="sm" className="gap-2">
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">New Case</span>
              </Button>
            }
          />
        </div>

        <div className="h-6 w-px bg-border" />

        {/* Admin Mode Toggle */}
        <button
          onClick={() => setIsAdminMode(!isAdminMode)}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
            isAdminMode
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
          )}
        >
          {isAdminMode ? (
            <ToggleRight className="w-4 h-4" />
          ) : (
            <ToggleLeft className="w-4 h-4" />
          )}
          {isAdminMode ? 'Admin Mode' : 'User Mode'}
        </button>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2">
              <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-accent-foreground" />
              </div>
              <span className="text-sm font-medium">{user}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem>
              <User className="w-4 h-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-destructive">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
