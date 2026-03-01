/**
 * Molecule — LoadingState
 *
 * Provides consistent loading skeleton layouts for various screen types.
 * Includes variants for lists, profiles, and dashboards.
 *
 * @example
 * ```tsx
 * // Basic list loading
 * <LoadingState cardCount={5} cardHeight={100} />
 *
 * // Profile loading
 * <ProfileLoadingState showAvatar={true} />
 *
 * // Dashboard loading
 * <DashboardLoadingState showQuickActions={true} />
 * ```
 */
import React from 'react';
import { View } from 'react-native';

import { Skeleton } from '@/components/atoms/skeleton';
import { LoadingStateProps, ProfileLoadingStateProps, DashboardLoadingStateProps } from './LoadingState.types';
import { styles } from './LoadingState.styles';

/** Default card count for LoadingState */
const DEFAULT_CARD_COUNT = 3;

/** Default card height for LoadingState */
const DEFAULT_CARD_HEIGHT = 80;

/** Default avatar size for ProfileLoadingState */
const AVATAR_SIZE = 80;

/** Default border radius for cards */
const CARD_BORDER_RADIUS = 16;

/**
 * Basic loading state showing a list of card skeletons.
 */
export function LoadingState({
  cardCount = DEFAULT_CARD_COUNT,
  cardHeight = DEFAULT_CARD_HEIGHT
}: LoadingStateProps) {
  return (
    <View style={styles.container}>
      {Array.from({ length: cardCount }).map((_, index) => (
        <Skeleton
          key={index}
          width="100%"
          height={cardHeight}
          borderRadius={CARD_BORDER_RADIUS}
        />
      ))}
    </View>
  );
}

/**
 * Loading state for profile screens with avatar and info skeletons.
 */
export function ProfileLoadingState({ showAvatar = true }: ProfileLoadingStateProps) {
  return (
    <View style={styles.profileContainer}>
      {showAvatar && (
        <View style={styles.avatarRow}>
          <Skeleton width={AVATAR_SIZE} height={AVATAR_SIZE} borderRadius={AVATAR_SIZE / 2} />
          <View style={styles.nameSkeletons}>
            <Skeleton width={200} height={24} />
            <Skeleton width={150} height={16} style={{ marginTop: 4 }} />
          </View>
        </View>
      )}
      <Skeleton width="100%" height={150} borderRadius={CARD_BORDER_RADIUS} />
      <Skeleton width="100%" height={150} borderRadius={CARD_BORDER_RADIUS} />
    </View>
  );
}

/**
 * Loading state for dashboard screens with quick actions and content sections.
 */
export function DashboardLoadingState({ showQuickActions = true }: DashboardLoadingStateProps) {
  return (
    <View style={styles.container}>
      {showQuickActions && (
        <View style={styles.section}>
          <Skeleton width={100} height={16} />
          <View style={styles.buttonRow}>
            <Skeleton width="48%" height={80} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={80} borderRadius={CARD_BORDER_RADIUS} />
          </View>
        </View>
      )}
      <View style={styles.section}>
        <Skeleton width={100} height={16} />
        <Skeleton width="100%" height={100} borderRadius={CARD_BORDER_RADIUS} />
        <Skeleton width="100%" height={100} borderRadius={CARD_BORDER_RADIUS} />
      </View>
    </View>
  );
}
