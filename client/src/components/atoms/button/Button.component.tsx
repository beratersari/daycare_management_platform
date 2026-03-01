/**
 * Atom — Button
 *
 * A reusable button component with multiple visual variants and loading state.
 * Supports primary (filled), secondary (outlined), and ghost (text-only) styles.
 *
 * @example
 * ```tsx
 * <Button label="Sign In" onPress={handleLogin} />
 * <Button label="Cancel" variant="ghost" onPress={handleCancel} />
 * <Button label="Loading..." isLoading={true} />
 * ```
 */
import React from 'react';
import { ActivityIndicator, Pressable } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { BrandColors } from '@/constants/theme';
import { ButtonProps } from './Button.types';
import { styles } from './Button.styles';

/** Primary brand color */
const PRIMARY_COLOR = BrandColors.coral;

/** Text color for primary buttons */
const PRIMARY_TEXT_COLOR = '#fff';

/** Default full width setting */
const DEFAULT_FULL_WIDTH = true;

export function Button({
  label,
  variant = 'primary',
  isLoading = false,
  fullWidth = DEFAULT_FULL_WIDTH,
  disabled,
  style,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || isLoading;
  const textColor = variant === 'primary' ? PRIMARY_TEXT_COLOR : PRIMARY_COLOR;

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
      accessibilityLabel={label}
      {...rest}>
      {isLoading ? (
        <ActivityIndicator color={textColor} size="small" />
      ) : (
        <AppText variant="subheading" color={textColor} style={styles.label}>
          {label}
        </AppText>
      )}
    </Pressable>
  );
}
