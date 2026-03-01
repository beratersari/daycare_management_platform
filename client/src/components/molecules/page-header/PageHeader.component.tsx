/**
 * Molecule — PageHeader
 *
 * A consistent header for management screens with a back button and title.
 * Provides optional right element slot for additional actions.
 *
 * @example
 * ```tsx
 * <PageHeader
 *   title="Manage Students"
 *   onBack={() => router.back()}
 *   rightElement={<Button label="Add" onPress={handleAdd} />}
 * />
 * ```
 */
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { useLocalization } from '@/hooks/use-localization';
import { PageHeaderProps } from './PageHeader.types';
import { styles } from './PageHeader.styles';

export function PageHeader({ title, onBack, rightElement }: PageHeaderProps) {
  const { t } = useLocalization();

  return (
    <View style={styles.header}>
      <Button
        label={t('common.back')}
        onPress={onBack}
        variant="ghost"
        style={styles.backButton}
      />
      <AppText variant="heading" style={styles.headerTitle}>
        {title}
      </AppText>
      {rightElement ?? <View style={styles.placeholder} />}
    </View>
  );
}
