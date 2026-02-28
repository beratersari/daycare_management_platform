/**
 * Molecule — InfoCard
 * A styled card for displaying information on the dashboard.
 */
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { useTheme } from '@/hooks/use-theme';

interface InfoCardProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
  rightElement?: React.ReactNode;
}

export function InfoCard({ title, subtitle, children, rightElement }: InfoCardProps) {
  const theme = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.backgroundElement }]}>
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
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerText: {
    flex: 1,
  },
  title: {
    fontWeight: '600',
  },
});
