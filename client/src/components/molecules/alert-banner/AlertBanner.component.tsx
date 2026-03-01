/**
 * Molecule — AlertBanner
 *
 * Displays a styled banner for error, success, or informational messages.
 * Commonly used below form fields or at the top of screens to provide feedback.
 *
 * @example
 * ```tsx
 * <AlertBanner type="error" message="Invalid credentials" />
 * <AlertBanner type="success" message="Account created successfully" />
 * <AlertBanner type="info" message="Please verify your email" />
 * ```
 */
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { AlertBannerProps } from './AlertBanner.types';
import { styles, ALERT_COLORS } from './AlertBanner.styles';

export function AlertBanner({ type, message }: AlertBannerProps) {
  const colorScheme = ALERT_COLORS[type];

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: colorScheme.bg, borderColor: colorScheme.border },
      ]}>
      <AppText variant="caption" color={colorScheme.text} style={styles.text}>
        {message}
      </AppText>
    </View>
  );
}
