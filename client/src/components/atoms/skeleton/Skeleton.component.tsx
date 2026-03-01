/**
 * Atom — Skeleton
 *
 * An animated placeholder component for loading states.
 * Displays a pulsing animation to indicate content is loading.
 *
 * @example
 * ```tsx
 * <Skeleton width="100%" height={80} borderRadius={16} />
 * <Skeleton width={200} height={24} />
 * ```
 */
import React, { useEffect, useRef } from 'react';
import { Animated, View } from 'react-native';

import { useTheme } from '@/hooks/use-theme';
import { SkeletonProps } from './Skeleton.types';
import { styles } from './Skeleton.styles';

/** Default border radius */
const DEFAULT_BORDER_RADIUS = 8;

/** Animation duration in milliseconds */
const ANIMATION_DURATION = 800;

/** Opacity values for the pulse animation */
const OPACITY_MIN = 0.3;
const OPACITY_MAX = 0.7;

export function Skeleton({
  width,
  height,
  borderRadius = DEFAULT_BORDER_RADIUS,
  style
}: SkeletonProps) {
  const theme = useTheme();
  const opacity = useRef(new Animated.Value(OPACITY_MIN)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: OPACITY_MAX,
          duration: ANIMATION_DURATION,
          useNativeDriver: true,
        }),
        Animated.timing(opacity, {
          toValue: OPACITY_MIN,
          duration: ANIMATION_DURATION,
          useNativeDriver: true,
        }),
      ])
    );
    animation.start();

    return () => animation.stop();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        styles.base,
        {
          width: width as any,
          height: height as any,
          borderRadius,
          backgroundColor: theme.backgroundSelected,
          opacity,
        },
        style,
      ]}
    />
  );
}
