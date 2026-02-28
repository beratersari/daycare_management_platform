/**
 * Design tokens for the Kinder Tracker app.
 * Colours, spacing, and font families used across all components.
 */
import { Platform } from 'react-native';

/**
 * Brand Colors - Primary palette for the app
 * #F26076 - Coral Pink (primary accent)
 * #FF9760 - Orange (secondary accent)
 * #FFD150 - Golden Yellow (tertiary accent)
 * #458B73 - Teal Green (success/action color)
 */
export const BrandColors = {
  coral: '#F26076',
  orange: '#FF9760',
  yellow: '#FFD150',
  teal: '#458B73',
} as const;

export const Colors = {
  light: {
    text: '#000000',
    background: '#ffffff',
    backgroundElement: '#F0F0F3',
    backgroundSelected: '#E0E1E6',
    textSecondary: '#60646C',
    // Brand colors
    primary: BrandColors.coral,
    secondary: BrandColors.orange,
    tertiary: BrandColors.yellow,
    success: BrandColors.teal,
  },
  dark: {
    text: '#ffffff',
    background: '#000000',
    backgroundElement: '#212225',
    backgroundSelected: '#2E3135',
    textSecondary: '#B0B4BA',
    // Brand colors (same in dark mode for consistency)
    primary: BrandColors.coral,
    secondary: BrandColors.orange,
    tertiary: BrandColors.yellow,
    success: BrandColors.teal,
  },
} as const;

export type ThemeColor = keyof typeof Colors.light & keyof typeof Colors.dark;

export const Fonts = Platform.select({
  ios: {
    sans: 'system-ui',
    serif: 'ui-serif',
    rounded: 'ui-rounded',
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: 'var(--font-display)',
    serif: 'var(--font-serif)',
    rounded: 'var(--font-rounded)',
    mono: 'var(--font-mono)',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;
