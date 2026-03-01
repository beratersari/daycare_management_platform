/**
 * Atom — AppText
 *
 * Base text component that respects the app theme.
 * Provides consistent typography through predefined variants.
 *
 * @example
 * ```tsx
 * <AppText variant="heading">Welcome</AppText>
 * <AppText variant="body" color={theme.textSecondary}>Description here</AppText>
 * <AppText variant="error">This field is required</AppText>
 * ```
 */
import React from 'react';
import { Text } from 'react-native';

import { useTheme } from '@/hooks/use-theme';
import { AppTextProps } from './AppText.types';
import { styles } from './AppText.styles';

/** Default color for error variant */
const ERROR_COLOR = '#EF4444';

export function AppText({
  variant = 'body',
  color,
  style,
  ...rest
}: AppTextProps) {
  const theme = useTheme();

  const resolvedColor = color ?? (variant === 'error' ? ERROR_COLOR : theme.text);

  return (
    <Text
      style={[styles[variant], { color: resolvedColor }, style]}
      {...rest}
    />
  );
}
