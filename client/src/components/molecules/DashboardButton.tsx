/**
 * Molecule — DashboardButton
 * A styled button for dashboard quick actions with brand colors.
 */
import React from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { BrandColors } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type ButtonColorVariant = 'coral' | 'orange' | 'yellow' | 'teal';

interface DashboardButtonProps {
  label: string;
  icon?: string;
  colorVariant?: ButtonColorVariant;
  onPress?: () => void;
  disabled?: boolean;
}

const COLOR_MAP: Record<ButtonColorVariant, string> = {
  coral: BrandColors.coral,
  orange: BrandColors.orange,
  yellow: BrandColors.yellow,
  teal: BrandColors.teal,
};

export function DashboardButton({
  label,
  icon,
  colorVariant = 'coral',
  onPress,
  disabled = false,
}: DashboardButtonProps) {
  const theme = useTheme();
  const bgColor = COLOR_MAP[colorVariant];

  return (
    <Pressable
      style={({ pressed }) => [
        styles.container,
        { backgroundColor: bgColor },
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
      ]}
      onPress={onPress}
      disabled={disabled || !onPress}
      accessibilityRole="button">
      {icon ? (
        <AppText variant="subheading" color="#fff" style={styles.icon}>
          {icon}
        </AppText>
      ) : null}
      <AppText variant="subheading" color="#fff" style={styles.label}>
        {label}
      </AppText>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    paddingVertical: 12,
    paddingHorizontal: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 72,
    flex: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 4,
    elevation: 3,
  },
  pressed: {
    opacity: 0.85,
    transform: [{ scale: 0.97 }],
  },
  disabled: {
    opacity: 0.5,
  },
  icon: {
    fontSize: 24,
    marginBottom: 4,
  },
  label: {
    textAlign: 'center',
    fontWeight: '600',
    fontSize: 13,
  },
});
