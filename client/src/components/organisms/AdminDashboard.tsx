/**
 * Organism — AdminDashboard
 * Dashboard view for admin users showing management tools.
 */
import { useRouter } from 'expo-router';
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { DashboardButton, ButtonColorVariant } from '@/components/molecules/DashboardButton';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useListTeachersQuery } from '@/store/api/teacherApi';
import { useListStudentsQuery } from '@/store/api/studentApi';
import { useListClassesQuery } from '@/store/api/classApi';
import { useListParentsQuery } from '@/store/api/parentApi';

export function AdminDashboard() {
  const theme = useTheme();
  const { t } = useLocalization();
  const router = useRouter();

  const { data: teachersData } = useListTeachersQuery({ pageSize: 1 });
  const { data: studentsData } = useListStudentsQuery({ pageSize: 1 });
  const { data: classesData } = useListClassesQuery({ pageSize: 1 });
  const { data: parentsData } = useListParentsQuery({ pageSize: 1 });

  return (
    <View style={styles.container}>
      {/* Management Tools */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.managementTools')}
        </AppText>
        <View style={styles.buttonGrid}>
          <DashboardButton
            label={t('dashboard.manageTeachers')}
            icon="👩‍🏫"
            colorVariant="coral"
            onPress={() => router.push('/manage/teachers')}
          />
          <DashboardButton
            label={t('dashboard.manageStudents')}
            icon="👶"
            colorVariant="orange"
            onPress={() => router.push('/manage/students')}
          />
          <DashboardButton
            label={t('dashboard.manageClasses')}
            icon="🏫"
            colorVariant="yellow"
            onPress={() => router.push('/manage/classes')}
          />
          <DashboardButton
            label={t('dashboard.manageParents')}
            icon="👨‍👩‍👧"
            colorVariant="teal"
            onPress={() => router.push('/manage/parents')}
          />
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.quickActions')}
        </AppText>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.reports')}
            icon="📊"
            colorVariant="coral"
            onPress={() => router.push('/manage/reports')}
          />
          <DashboardButton
            label={t('dashboard.announcements')}
            icon="📢"
            colorVariant="orange"
            onPress={() => router.push('/manage/announcements')}
          />
        </View>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.events')}
            icon="🎉"
            colorVariant="yellow"
            onPress={() => router.push('/manage/events')}
          />
          <DashboardButton
            label={t('dashboard.mealMenus')}
            icon="🍽️"
            colorVariant="teal"
            onPress={() => router.push('/manage/meal-menus')}
          />
        </View>
      </View>

      {/* Overview Stats */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          Overview
        </AppText>
        <View style={styles.statsRow}>
          <StatCard label="Teachers" value={teachersData?.total.toString() || '—'} color="coral" />
          <StatCard label="Students" value={studentsData?.total.toString() || '—'} color="orange" />
        </View>
        <View style={styles.statsRow}>
          <StatCard label="Classes" value={classesData?.total.toString() || '—'} color="yellow" />
          <StatCard label="Parents" value={parentsData?.total.toString() || '—'} color="teal" />
        </View>
      </View>
    </View>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color: ButtonColorVariant }) {
  const theme = useTheme();
  const colorMap: Record<ButtonColorVariant, string> = {
    coral: '#F26076',
    orange: '#FF9760',
    yellow: '#FFD150',
    teal: '#458B73',
  };

  return (
    <View style={[styles.statCard, { backgroundColor: theme.backgroundElement }]}>
      <AppText variant="display" color={colorMap[color]} style={styles.statValue}>
        {value}
      </AppText>
      <AppText variant="caption" color={theme.textSecondary}>
        {label}
      </AppText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 20,
  },
  section: {
    gap: 12,
  },
  sectionLabel: {
    marginBottom: 4,
    fontSize: 13,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 10,
  },
  statCard: {
    flex: 1,
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 8,
    alignItems: 'center',
    minHeight: 80,
    justifyContent: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
  },
});
