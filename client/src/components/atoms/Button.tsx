/**
 * Atom — Button
 * Reusable button with primary / secondary / ghost variants and loading state.
 */
import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  type PressableProps,
  type ViewStyle,
} from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { BrandColors } from '@/constants/theme';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost';

export interface ButtonProps extends PressableProps {
  label: string;
  variant?: ButtonVariant;
  isLoading?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
}

// Use brand colors for button styling
const PRIMARY = BrandColors.coral;
const PRIMARY_DARK = '#D94D5F';

export function Button({
  label,
  variant = 'primary',
  isLoading = false,
  fullWidth = true,
  disabled,
  style,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || isLoading;

  return (
    <Pressable
      style={({ pressed }) => [
        styles.base,
        fullWidth && styles.fullWidth,
        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'ghost' && styles.ghost,
        isDisabled && styles.disabled,
        pressed && !isDisabled && styles.pressed,
        style,
      ]}
      disabled={isDisabled}
      accessibilityRole="button"
      {...rest}>
      {isLoading ? (
        <ActivityIndicator
          color={variant === 'primary' ? '#fff' : PRIMARY}
          size="small"
        />
      ) : (
        <AppText
          variant="subheading"
          color={variant === 'primary' ? '#fff' : PRIMARY}
          style={styles.label}>
          {label}
        </AppText>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    height: 52,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  fullWidth: {
    alignSelf: 'stretch',
  },
  primary: {
    backgroundColor: PRIMARY,
  },
  secondary: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: PRIMARY,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  disabled: {
    opacity: 0.5,
  },
  pressed: {
    opacity: 0.85,
    transform: [{ scale: 0.98 }],
  },
  label: {
    fontWeight: '600',
  },
});
