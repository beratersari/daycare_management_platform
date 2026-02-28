/**
 * Atom — Logo
 * App logo mark with the Kinder Tracker brand colour.
 */
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { BrandColors } from '@/constants/theme';

// Use the coral brand color for the logo
const BRAND = BrandColors.coral;

export function Logo() {
  return (
    <View style={styles.container}>
      {/* Simple geometric mark: two overlapping circles */}
      <View style={styles.mark}>
        <View style={[styles.circle, styles.circleLeft]} />
        <View style={[styles.circle, styles.circleRight]} />
        <AppText variant="display" color="#fff" style={styles.emoji}>
          🎒
        </AppText>
      </View>
      <AppText variant="heading" color={BRAND} style={styles.wordmark}>
        Kinder Tracker
      </AppText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    gap: 16,
  },
  mark: {
    width: 96,
    height: 96,
    borderRadius: 28,
    backgroundColor: BRAND,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: BRAND,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 10,
  },
  circle: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.15)',
  },
  circleLeft: { top: 8, left: 8 },
  circleRight: { bottom: 8, right: 8 },
  emoji: {
    fontSize: 44,
    lineHeight: 52,
  },
  wordmark: {
    letterSpacing: -0.3,
  },
});
