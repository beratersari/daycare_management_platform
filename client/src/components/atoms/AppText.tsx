/**
 * Atom — AppText
 * Base text component that respects the app theme.
 */
import React from 'react';
import { StyleSheet, Text, type TextProps } from 'react-native';

import { useTheme } from '@/hooks/use-theme';

export type TextVariant =
  | 'display'
  | 'heading'
  | 'subheading'
  | 'body'
  | 'caption'
  | 'label'
  | 'error';

export interface AppTextProps extends TextProps {
  variant?: TextVariant;
  color?: string;
}

export function AppText({
  variant = 'body',
  color,
  style,
  ...rest
}: AppTextProps) {
  const theme = useTheme();

  const resolvedColor =
    color ?? (variant === 'error' ? '#EF4444' : theme.text);

  return (
    <Text
      style={[styles[variant], { color: resolvedColor }, style]}
      {...rest}
    />
  );
}

const styles = StyleSheet.create({
  display: {
    fontSize: 32,
    fontWeight: '700',
    lineHeight: 40,
    letterSpacing: -0.5,
  },
  heading: {
    fontSize: 22,
    fontWeight: '700',
    lineHeight: 30,
  },
  subheading: {
    fontSize: 17,
    fontWeight: '600',
    lineHeight: 24,
  },
  body: {
    fontSize: 15,
    fontWeight: '400',
    lineHeight: 22,
  },
  caption: {
    fontSize: 13,
    fontWeight: '400',
    lineHeight: 18,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    lineHeight: 18,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  error: {
    fontSize: 13,
    fontWeight: '500',
    lineHeight: 18,
  },
});
