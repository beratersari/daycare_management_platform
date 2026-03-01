/**
 * Atom — Logo
 *
 * App logo mark with the Kinder Tracker brand styling.
 * Displays a rounded square with decorative circles and a backpack emoji.
 *
 * @example
 * ```tsx
 * <Logo />
 * ```
 */
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { BrandColors } from '@/constants/theme';
import { LogoProps } from './Logo.types';
import { styles } from './Logo.styles';

/** Primary brand color */
const BRAND_COLOR = BrandColors.coral;

/** Emoji displayed in the logo */
const LOGO_EMOJI = '🎒';

/** App name displayed below the logo */
const APP_NAME = 'Kinder Tracker';

export function Logo(_props: LogoProps) {
  return (
    <View style={styles.container}>
      <View style={styles.mark}>
        <View style={[styles.circle, styles.circleLeft]} />
        <View style={[styles.circle, styles.circleRight]} />
        <AppText variant="display" color="#fff" style={styles.emoji}>
          {LOGO_EMOJI}
        </AppText>
      </View>
      <AppText variant="heading" color={BRAND_COLOR} style={styles.wordmark}>
        {APP_NAME}
      </AppText>
    </View>
  );
}
