/**
 * Molecule — InfoCard
 *
 * A styled card for displaying information with optional press interaction.
 * Features a header with title, subtitle, and optional right element,
 * with additional content rendered below.
 *
 * @example
 * ```tsx
 * // Basic card
 * <InfoCard title="John Doe" subtitle="Date of Birth: 2020-01-15" />
 *
 * // Pressable card with children
 * <InfoCard
 *   title="Class A"
 *   subtitle="Room 101"
 *   onPress={() => router.push('/class/1')}
 * >
 *   <AppText>Capacity: 20 students</AppText>
 * </InfoCard>
 *
 * // Card with right element
 * <InfoCard title="Student" rightElement={<Icon name="chevron-forward" />}>
 *   ...
 * </InfoCard>
 * ```
 */
import React from 'react';
import { Pressable, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { useTheme } from '@/hooks/use-theme';
import { InfoCardProps } from './InfoCard.types';
import { styles } from './InfoCard.styles';

export function InfoCard({ title, subtitle, children, rightElement, onPress }: InfoCardProps) {
  const theme = useTheme();

  const renderContent = () => (
    <>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <AppText variant="subheading" style={styles.title}>
            {title}
          </AppText>
          {subtitle ? (
            <AppText variant="caption" color={theme.textSecondary}>
              {subtitle}
            </AppText>
          ) : null}
        </View>
        {rightElement}
      </View>
      {children}
    </>
  );

  if (onPress) {
    return (
      <Pressable
        style={({ pressed }) => [
          styles.container,
          { backgroundColor: theme.backgroundElement },
          pressed && styles.pressed,
        ]}
        onPress={onPress}
        accessibilityRole="button"
        accessibilityLabel={title}>
        {renderContent()}
      </Pressable>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.backgroundElement }]}>
      {renderContent()}
    </View>
  );
}
