/**
 * Atom — Icon
 *
 * A wrapper around @expo/vector-icons Ionicons for consistent icon usage.
 * Provides type-safe icon names and default sizing.
 *
 * @example
 * ```tsx
 * <Icon name="school" size={24} color="#F26076" />
 * <Icon name="calendar" color={theme.textSecondary} />
 * ```
 */
import React from 'react';
import Ionicons from '@expo/vector-icons/Ionicons';

import { IconProps } from './Icon.types';
import { styles } from './Icon.styles';

/** Default icon size in pixels */
const DEFAULT_SIZE = 24;

/** Default icon color (black) */
const DEFAULT_COLOR = '#000';

export function Icon({
  name,
  size = DEFAULT_SIZE,
  color = DEFAULT_COLOR,
  style
}: IconProps) {
  return (
    <Ionicons
      name={name}
      size={size}
      color={color}
      style={[styles.icon, style]}
    />
  );
}