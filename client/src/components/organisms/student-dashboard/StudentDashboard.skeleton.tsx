/**
 * StudentDashboardSkeleton
 * Loading skeleton for the StudentDashboard component.
 */
import React from 'react';
import { View } from 'react-native';

import { Skeleton } from '@/components/atoms/skeleton';
import { styles } from './StudentDashboard.styles';

/** Skeleton dimensions */
const SECTION_LABEL_WIDTH = 120;
const BUTTON_HEIGHT = 72;
const CARD_BORDER_RADIUS = 16;
const CLASS_CARD_HEIGHT = 100;

interface StudentDashboardSkeletonProps {
  /** Whether to show the quick actions section. Defaults to true */
  showQuickActions?: boolean;
  /** Whether to show the classes section. Defaults to true */
  showClasses?: boolean;
  /** Number of class cards to show. Defaults to 2 */
  classCount?: number;
}

export function StudentDashboardSkeleton({
  showQuickActions = true,
  showClasses = true,
  classCount = 2,
}: StudentDashboardSkeletonProps) {
  return (
    <View style={styles.container}>
      {showQuickActions && (
        <View style={styles.section}>
          <Skeleton width={SECTION_LABEL_WIDTH} height={16} style={{ marginBottom: 8 }} />
          <View style={styles.buttonRow}>
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
            <Skeleton width="48%" height={BUTTON_HEIGHT} borderRadius={CARD_BORDER_RADIUS} />
          </View>
        </View>
      )}

      {showClasses && (
        <View style={styles.section}>
          <Skeleton width={SECTION_LABEL_WIDTH} height={16} style={{ marginBottom: 8 }} />
          {Array.from({ length: classCount }).map((_, index) => (
            <Skeleton
              key={`class-${index}`}
              width="100%"
              height={CLASS_CARD_HEIGHT}
              borderRadius={CARD_BORDER_RADIUS}
              style={{ marginBottom: 12 }}
            />
          ))}
        </View>
      )}
    </View>
  );
}