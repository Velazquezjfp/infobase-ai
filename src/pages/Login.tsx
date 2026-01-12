import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '@/contexts/AppContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FolderOpen, Shield, FileText, Bot } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import i18n from '@/i18n/config';

export default function Login() {
  const [name, setName] = useState('');
  const { setUser } = useApp();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState<'de' | 'en'>('de');

  // S5-014: Initialize language from localStorage on mount
  useEffect(() => {
    const storedLanguage = localStorage.getItem('bamf_language');
    if (storedLanguage === 'en' || storedLanguage === 'de') {
      setCurrentLanguage(storedLanguage);
      i18n.changeLanguage(storedLanguage);
    }
  }, []);

  // S5-014: Toggle language and persist to localStorage
  const toggleLanguage = () => {
    const newLang = currentLanguage === 'de' ? 'en' : 'de';
    setCurrentLanguage(newLang);
    localStorage.setItem('bamf_language', newLang);
    i18n.changeLanguage(newLang);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      setUser(name.trim());
      navigate('/workspace');
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary via-primary to-primary/80" />
        <div className="relative z-10 flex flex-col justify-center p-12 text-primary-foreground">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-primary-foreground/10 rounded-lg flex items-center justify-center">
                <Shield className="w-7 h-7" />
              </div>
              <span className="text-2xl font-semibold">BAMF</span>
            </div>
            <h1 className="text-4xl font-bold leading-tight mb-4">
              {t('login.title')}
            </h1>
            <p className="text-lg text-primary-foreground/80 max-w-md">
              {t('login.subtitle')}
            </p>
          </div>

          <div className="space-y-4 mt-8">
            <div className="flex items-center gap-4 p-4 bg-primary-foreground/5 rounded-lg">
              <FolderOpen className="w-6 h-6 text-primary-foreground/70" />
              <div>
                <p className="font-medium">{t('login.feature1Title')}</p>
                <p className="text-sm text-primary-foreground/60">{t('login.feature1Description')}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-primary-foreground/5 rounded-lg">
              <FileText className="w-6 h-6 text-primary-foreground/70" />
              <div>
                <p className="font-medium">{t('login.feature2Title')}</p>
                <p className="text-sm text-primary-foreground/60">{t('login.feature2Description')}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-primary-foreground/5 rounded-lg">
              <Bot className="w-6 h-6 text-primary-foreground/70" />
              <div>
                <p className="font-medium">{t('login.feature3Title')}</p>
                <p className="text-sm text-primary-foreground/60">{t('login.feature3Description')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* S5-014: Language Toggle Button */}
          <div className="flex justify-end mb-4">
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors bg-secondary text-secondary-foreground hover:bg-secondary/80"
              title={t('language.switchLanguage')}
            >
              {currentLanguage === 'de' ? (
                <>
                  <span>🇬🇧</span>
                  <span>EN</span>
                </>
              ) : (
                <>
                  <span>🇩🇪</span>
                  <span>DE</span>
                </>
              )}
            </button>
          </div>

          <div className="lg:hidden mb-8 text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Shield className="w-8 h-8 text-primary" />
              <span className="text-xl font-semibold text-primary">BAMF</span>
            </div>
            <h1 className="text-2xl font-bold text-foreground">{t('login.title')}</h1>
          </div>

          <div className="bg-card p-8 rounded-xl border border-border shadow-sm">
            <h2 className="text-2xl font-semibold text-foreground mb-2">{t('login.welcome')}</h2>
            <p className="text-muted-foreground mb-6">{t('login.enterNamePrompt')}</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-foreground mb-2">
                  {t('login.yourName')}
                </label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t('login.namePlaceholder')}
                  className="w-full h-12"
                  autoFocus
                />
              </div>
              <Button
                type="submit"
                className="w-full h-12 text-base font-medium"
                disabled={!name.trim()}
              >
                {t('login.enterWorkspace')}
              </Button>
            </form>
          </div>

          <p className="text-center text-sm text-muted-foreground mt-6">
            {t('login.footer')}
          </p>
        </div>
      </div>
    </div>
  );
}
