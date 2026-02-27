/**
 * Molecule — AlertBanner
 * Displays an error or success message banner below form fields.
 */
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';

export type AlertType = 'error' | 'success' | 'info';

interface AlertBannerProps {
  type: AlertType;
  message: string;
}

const COLORS: Record<AlertType, { bg: string; text: string; border: string }> =
  {
    error: { bg: '#FEF2F2', text: '#B91C1C', border: '#FECACA' },
    success: { bg: '#F0FDF4', text: '#15803D', border: '#BBF7D0' },
    info: { bg: '#EFF6FF', text: '#1D4ED8', border: '#BFDBFE' },
  };

export function AlertBanner({ type, message }: AlertBannerProps) {
  const c = COLORS[type];
  return (
    <View
      style={[
        styles.container,
        { backgroundColor: c.bg, borderColor: c.border },
      ]}>
      <AppText variant="caption" color={c.text} style={styles.text}>
        {message}
      </AppText>
    </View>
  );
}

const styles = StyleSheet.create({
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
