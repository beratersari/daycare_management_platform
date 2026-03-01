/**
 * Organism — StudentDashboard
 * Dashboard view for student users showing their classes.
 */
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Skeleton } from '@/components/atoms/skeleton';
import { InfoCard } from '@/components/molecules/info-card';
import { DashboardButton } from '@/components/molecules/dashboard-button';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useListClassesQuery } from '@/store/api/classApi';
import { StudentDashboardProps } from './StudentDashboard.types';
import { styles } from './StudentDashboard.styles';

export function StudentDashboard(_props: StudentDashboardProps) {
  const theme = useTheme();
  const { t } = useLocalization();
  const { data: classesData, isLoading } = useListClassesQuery({ pageSize: 10 });

  if (isLoading) {
    return (
      <View style={styles.container}>
        <View style={styles.section}>
          <Skeleton width={100} height={16} />
          <View style={styles.buttonRow}>
            <Skeleton width="48%" height={80} borderRadius={16} />
            <Skeleton width="48%" height={80} borderRadius={16} />
          </View>
        </View>
        <View style={styles.section}>
          <Skeleton width={100} height={16} />
          <Skeleton width="100%" height={100} borderRadius={16} />
          <Skeleton width="100%" height={100} borderRadius={16} />
        </View>
      </View>
    );
  }

  const classes = classesData?.data || [];

  return (
    <View style={styles.container}>
      {/* Quick Actions */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.quickActions')}
        </AppText>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.events')}
            icon="calendar"
            colorVariant="orange"
          />
          <DashboardButton
            label={t('dashboard.mealMenus')}
            icon="restaurant"
            colorVariant="yellow"
          />
        </View>
      </View>

      {/* My Classes */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.myClasses')}
        </AppText>
        {classes.length > 0 ? (
          classes.map((cls) => (
            <InfoCard
              key={cls.class_id}
              title={cls.class_name}
              subtitle={`${t('class.room')}: ${cls.room_number || 'N/A'}`}
            >
              <View style={styles.classDetails}>
                <AppText variant="caption" color={theme.textSecondary}>
                  {t('class.capacity')}: {cls.capacity}
                </AppText>
                {cls.schedule && (
                  <AppText variant="caption" color={theme.textSecondary}>
                    {t('class.schedule')}: {cls.schedule}
                  </AppText>
                )}
              </View>
            </InfoCard>
          ))
        ) : (
          <InfoCard title={t('dashboard.noClasses')} />
        )}
      </View>
    </View>
  );
}
