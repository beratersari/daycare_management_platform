/**
 * Template — ScreenTemplate
 *
 * Standard layout for management and detail screens.
 * Provides consistent structure with optional header and scrollable content.
 *
 * @example
 * ```tsx
 * <ScreenTemplate
 *   header={<PageHeader title="Manage Students" onBack={() => router.back()} />}
 * >
 *   <LoadingState />
 * </ScreenTemplate>
 * ```
 */
import React from 'react';
import { ScrollView, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useTheme } from '@/hooks/use-theme';
import { ScreenTemplateProps } from './ScreenTemplate.types';
import { styles } from './ScreenTemplate.styles';

/** Default scrollable setting */
const DEFAULT_SCROLLABLE = true;

export function ScreenTemplate({
  header,
  children,
  scrollable = DEFAULT_SCROLLABLE,
}: ScreenTemplateProps) {
  const theme = useTheme();

  return (
    <SafeAreaView
      style={[styles.safe, { backgroundColor: theme.background }]}
      edges={['top', 'bottom']}>
      {header}
      {scrollable ? (
        <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
          {children}
        </ScrollView>
      ) : (
        <View style={styles.nonScrollContent}>
          {children}
        </View>
      )}
    </SafeAreaView>
  );
}
