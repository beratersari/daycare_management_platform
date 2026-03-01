import { StyleSheet } from 'react-native';
import { AlertType } from './AlertBanner.types';

/**
 * Color configuration for each alert type.
 * Contains background, text, and border colors for consistent styling.
 */
export const ALERT_COLORS: Record<AlertType, { bg: string; text: string; border: string }> = {
  error: { bg: '#FEF2F2', text: '#B91C1C', border: '#FECACA' },
  success: { bg: '#F0FDF4', text: '#15803D', border: '#BBF7D0' },
  info: { bg: '#EFF6FF', text: '#1D4ED8', border: '#BFDBFE' },
};

export const styles = StyleSheet.create({
  container: {
    borderRadius: 10,
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 10,
    alignSelf: 'stretch',
  },
  text: {
    fontWeight: '500',
  },
});
