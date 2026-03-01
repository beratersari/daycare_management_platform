import { StyleSheet } from 'react-native';
import { BrandColors } from '@/constants/theme';

/** Primary brand color */
const BRAND_COLOR = BrandColors.coral;

/** Logo mark size */
const MARK_SIZE = 96;

/** Circle decoration size */
const CIRCLE_SIZE = 40;

/** Emoji size */
const EMOJI_SIZE = 44;

export const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    gap: 16,
  },
  mark: {
    width: MARK_SIZE,
    height: MARK_SIZE,
    borderRadius: 28,
    backgroundColor: BRAND_COLOR,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: BRAND_COLOR,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 10,
  },
  circle: {
    position: 'absolute',
    width: CIRCLE_SIZE,
    height: CIRCLE_SIZE,
    borderRadius: CIRCLE_SIZE / 2,
    backgroundColor: 'rgba(255,255,255,0.15)',
  },
  circleLeft: { top: 8, left: 8 },
  circleRight: { bottom: 8, right: 8 },
  emoji: {
    fontSize: EMOJI_SIZE,
    lineHeight: 52,
  },
  wordmark: {
    letterSpacing: -0.3,
  },
});
