/**
 * React hook for accessing localization in components.
 */
import { useCallback } from 'react';
import { t, getTranslations, getCurrentLanguage, setLanguage, type LanguageCode } from '@/localization';

export function useLocalization() {
  const translate = useCallback((keyPath: string, vars?: Record<string, string | number>) => {
    return t(keyPath, vars);
  }, []);

  const translations = getTranslations();
  const currentLang = getCurrentLanguage();

  const changeLanguage = useCallback((lang: LanguageCode) => {
    setLanguage(lang);
  }, []);

  return {
    t: translate,
    translations,
    currentLanguage: currentLang,
    setLanguage: changeLanguage,
  };
}
