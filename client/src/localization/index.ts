/**
 * Localization system for the Kinder Tracker app.
 * Provides a simple i18n (internationalization) solution.
 */
import { en, type Translations } from './en';

export type LanguageCode = 'en';

const translations: Record<LanguageCode, Translations> = {
  en,
};

let currentLanguage: LanguageCode = 'en';

/**
 * Get the current language code.
 */
export function getCurrentLanguage(): LanguageCode {
  return currentLanguage;
}

/**
 * Set the current language.
 */
export function setLanguage(lang: LanguageCode): void {
  if (translations[lang]) {
    currentLanguage = lang;
  }
}

/**
 * Get a translation by key path (e.g., 'auth.signIn').
 * Supports interpolation with {variable} syntax.
 */
export function t(keyPath: string, vars?: Record<string, string | number>): string {
  const keys = keyPath.split('.');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let value: any = translations[currentLanguage];

  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      // Key not found, return the key path as fallback
      return keyPath;
    }
  }

  if (typeof value !== 'string') {
    return keyPath;
  }

  // Interpolate variables
  if (vars) {
    return Object.entries(vars).reduce((str, [k, v]) => {
      return str.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
    }, value);
  }

  return value;
}

/**
 * Get all translations for the current language.
 */
export function getTranslations(): Translations {
  return translations[currentLanguage];
}

export { en, type Translations };
