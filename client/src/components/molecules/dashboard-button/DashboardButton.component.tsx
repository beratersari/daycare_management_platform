/**
 * Molecule — DashboardButton
 *
 * A styled button for dashboard quick actions with brand colors.
 * Features an optional icon, customizable color variant, and press feedback.
 *
 * @example
 * ```tsx
 * <DashboardButton
 *   label="Manage Teachers"
 *   icon="school"
 *   colorVariant="coral"
 *   onPress={() => router.push('/manage/teachers')}
 * />
 * ```
 */
import React from 'react';
import { Pressable } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Icon } from '@/components/atoms/icon';
import { DashboardButtonProps } from './DashboardButton.types';
import { styles, VARIANT_COLORS } from './DashboardButton.styles';

/** Default icon size for dashboard buttons */
const ICON_SIZE = 24;

/** Default icon color (white for visibility on colored backgrounds) */
const ICON_COLOR = '#fff';

export function DashboardButton({
  label,
  icon,
  colorVariant = 'coral',
  onPress,
  disabled = false,
}: DashboardButtonProps) {
  const backgroundColor = VARIANT_COLORS[colorVariant];
  const isButtonDisabled = disabled || !onPress;

  return (
    <Pressable
      style={({ pressed }) => [
        styles.container,
        { backgroundColor },
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
      ]}
      onPress={onPress}
      disabled={isButtonDisabled}
      accessibilityRole="button"
      accessibilityLabel={label}>
      {icon ? (
        <Icon name={icon} size={ICON_SIZE} color={ICON_COLOR} style={styles.icon} />
      ) : null}
      <AppText variant="subheading" color="#fff" style={styles.label}>
        {label}
      </AppText>
    </Pressable>
  );
}
