/**
 * Organism — AdminDashboard
 *
 * Dashboard view for admin and director users showing management tools,
 * quick actions, and overview statistics.
 *
 * @example
 * ```tsx
 * <AdminDashboard />
 * ```
 */
import { useRouter } from 'expo-router';
import React, { useEffect, useMemo, useState } from 'react';
import { Pressable, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { DashboardButton, ButtonColorVariant } from '@/components/molecules/dashboard-button';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useListTeachersQuery } from '@/store/api/teacherApi';
import { useListStudentsQuery } from '@/store/api/studentApi';
import { useListClassesQuery } from '@/store/api/classApi';
import { useListParentsQuery } from '@/store/api/parentApi';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { BrandColors } from '@/constants/theme';
import { AdminDashboardProps } from './AdminDashboard.types';
import { styles } from './AdminDashboard.styles';

/** Color mapping for stat cards */
const STAT_COLORS: Record<ButtonColorVariant, string> = {
  coral: '#F26076',
  orange: '#FF9760',
  yellow: '#FFD150',
  teal: '#458B73',
};

/** Default placeholder for missing stat values */
const MISSING_VALUE_PLACEHOLDER = '—';

interface StatCardProps {
  /** Label describing the stat */
  label: string;
  /** The stat value to display */
  value: string;
  /** Color variant for the value text */
  color: ButtonColorVariant;
}

/**
 * Internal component for displaying a statistic card.
 */
function StatCard({ label, value, color }: StatCardProps) {
  const theme = useTheme();

  return (
    <View style={[styles.statCard, { backgroundColor: theme.backgroundElement }]}>
      <AppText variant="display" color={STAT_COLORS[color]} style={styles.statValue}>
        {value}
      </AppText>
      <AppText variant="caption" color={theme.textSecondary}>
        {label}
      </AppText>
    </View>
  );
}

export function AdminDashboard(_props: AdminDashboardProps) {
  const theme = useTheme();
  const { t } = useLocalization();
  const router = useRouter();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;

  const [selectedSchoolId, setSelectedSchoolId] = useState<number | undefined>(user?.school_id || undefined);

  const shouldLoadSchools = userRole === 'ADMIN' || userRole === 'DIRECTOR';

  const { data: schools } = useListSchoolsQuery(undefined, {
    skip: !shouldLoadSchools,
  });

  useEffect(() => {
    if (userRole === 'ADMIN' && schools && schools.length > 0 && !selectedSchoolId) {
      setSelectedSchoolId(schools[0].school_id);
    }
  }, [schools, userRole, selectedSchoolId]);

  const selectedSchool = useMemo(() => {
    if (userRole === 'ADMIN') {
      return schools?.find((school) => school.school_id === selectedSchoolId) ?? null;
    }
    if (user?.school_id) {
      return schools?.find((school) => school.school_id === user.school_id) ?? null;
    }
    return null;
  }, [schools, selectedSchoolId, userRole, user?.school_id]);

  // Fetch overview statistics
  const { data: teachersData } = useListTeachersQuery({ pageSize: 1 });
  const { data: studentsData } = useListStudentsQuery({ pageSize: 1 });
  const { data: classesData } = useListClassesQuery({ pageSize: 1 });
  const { data: parentsData } = useListParentsQuery({ pageSize: 1 });

  const getStatValue = (count: number | undefined): string => {
    return count?.toString() ?? MISSING_VALUE_PLACEHOLDER;
  };

  return (
    <View style={styles.container}>
      {(userRole === 'ADMIN' || userRole === 'DIRECTOR') && selectedSchool ? (
        <View style={styles.section}>
          <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
            {t('dashboard.managingSchool')}
          </AppText>
          {userRole === 'ADMIN' && schools && schools.length > 0 ? (
            <View style={styles.selectorRow}>
              {schools.map((school) => (
                <Pressable
                  key={school.school_id}
                  onPress={() => setSelectedSchoolId(school.school_id)}
                  style={[
                    styles.selectorButton,
                    selectedSchoolId === school.school_id && { backgroundColor: BrandColors.coral },
                  ]}
                >
                  <AppText
                    variant="caption"
                    color={selectedSchoolId === school.school_id ? '#fff' : theme.text}
                  >
                    {school.school_name}
                  </AppText>
                </Pressable>
              ))}
            </View>
          ) : (
            <View style={[styles.selectedSchoolCard, { backgroundColor: theme.backgroundElement }]}>
              <AppText variant="body">{selectedSchool.school_name}</AppText>
              {selectedSchool.address ? (
                <AppText variant="caption" color={theme.textSecondary}>
                  {selectedSchool.address}
                </AppText>
              ) : null}
            </View>
          )}
        </View>
      ) : null}

      {/* Management Tools */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.managementTools')}
        </AppText>
        <View style={styles.buttonGrid}>
          <DashboardButton
            label={t('dashboard.manageTeachers')}
            icon="school"
            colorVariant="coral"
            onPress={() => router.push('/manage/teachers')}
          />
          <DashboardButton
            label={t('dashboard.manageStudents')}
            icon="happy"
            colorVariant="orange"
            onPress={() => router.push('/manage/students')}
          />
          <DashboardButton
            label={t('dashboard.manageClasses')}
            icon="library"
            colorVariant="yellow"
            onPress={() => router.push('/manage/classes')}
          />
          <DashboardButton
            label={t('dashboard.manageParents')}
            icon="people"
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
            icon="bar-chart"
            colorVariant="coral"
            onPress={() => router.push('/manage/reports')}
          />
          <DashboardButton
            label={t('dashboard.announcements')}
            icon="megaphone"
            colorVariant="orange"
            onPress={() => router.push('/manage/announcements')}
          />
        </View>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.events')}
            icon="calendar"
            colorVariant="yellow"
            onPress={() => router.push('/manage/events')}
          />
          <DashboardButton
            label={t('dashboard.mealMenus')}
            icon="restaurant"
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
          <StatCard label="Teachers" value={getStatValue(teachersData?.total)} color="coral" />
          <StatCard label="Students" value={getStatValue(studentsData?.total)} color="orange" />
        </View>
        <View style={styles.statsRow}>
          <StatCard label="Classes" value={getStatValue(classesData?.total)} color="yellow" />
          <StatCard label="Parents" value={getStatValue(parentsData?.total)} color="teal" />
        </View>
      </View>
    </View>
  );
}
