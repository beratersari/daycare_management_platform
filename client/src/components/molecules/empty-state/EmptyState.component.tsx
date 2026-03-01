/**
 * Molecule — EmptyState
 *
 * Displays a consistent placeholder for empty lists and screens.
 * Shows an optional icon or emoji, a main message, and an optional subtitle.
 *
 * @example
 * ```tsx
 * <EmptyState
 *   icon="list"
 *   message="No students found"
 *   subtitle="Add your first student to get started"
 * />
 * ```
 */
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Icon } from '@/components/atoms/icon';
import { useTheme } from '@/hooks/use-theme';
import { EmptyStateProps } from './EmptyState.types';
import { styles } from './EmptyState.styles';

/** Default icon size for empty state icons */
const ICON_SIZE = 48;

export function EmptyState({ message, icon, emoji, subtitle }: EmptyStateProps) {
  const theme = useTheme();

  return (
    <View style={styles.container}>
      {icon ? (
        <Icon name={icon} size={ICON_SIZE} color={theme.textSecondary} style={styles.icon} />
      ) : emoji ? (
        <AppText variant="display" style={styles.emoji}>
          {emoji}
        </AppText>
      ) : null}
      <AppText variant="subheading" style={styles.message}>
        {message}
      </AppText>
      {subtitle && (
        <AppText variant="body" color={theme.textSecondary} style={styles.subtitle}>
          {subtitle}
        </AppText>
      )}
    </View>
  );
}
