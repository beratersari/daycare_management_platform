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

export type ButtonVariant = 'primary' | 'secondary' | 'ghost';

export interface ButtonProps extends PressableProps {
  label: string;
  variant?: ButtonVariant;
  isLoading?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
}

const BRAND = '#208AEF';
const BRAND_DARK = '#1A70C8';

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
          color={variant === 'primary' ? '#fff' : BRAND}
          size="small"
        />
      ) : (
        <AppText
          variant="subheading"
          color={variant === 'primary' ? '#fff' : BRAND}
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
    backgroundColor: BRAND,
  },
  secondary: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: BRAND,
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
