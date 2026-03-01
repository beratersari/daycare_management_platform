/**
 * Organism — TeacherDashboard
 * Dashboard view for teacher users showing students in their classes.
 */
import { useRouter } from 'expo-router';
import React from 'react';
import { View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Skeleton } from '@/components/atoms/skeleton';
import { Icon } from '@/components/atoms/icon';
import { InfoCard } from '@/components/molecules/info-card';
import { DashboardButton } from '@/components/molecules/dashboard-button';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useGetMyStudentsQuery } from '@/store/api/teacherApi';
import { useGetTeacherClassesQuery } from '@/store/api/teacherApi';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { BrandColors } from '@/constants/theme';
import { TeacherDashboardProps } from './TeacherDashboard.types';
import { styles } from './TeacherDashboard.styles';

export function TeacherDashboard(_props: TeacherDashboardProps) {
  const theme = useTheme();
  const { t } = useLocalization();
  const router = useRouter();
  const user = useAppSelector(selectCurrentUser);
  
  const { data: students, isLoading: studentsLoading } = useGetMyStudentsQuery();
  const { data: classes, isLoading: classesLoading } = useGetTeacherClassesQuery(user?.user_id || 0, {
    skip: !user?.user_id,
  });

  const isLoading = studentsLoading || classesLoading;

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
        </View>
        <View style={styles.section}>
          <Skeleton width={100} height={16} />
          <Skeleton width="100%" height={100} borderRadius={16} />
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Quick Actions */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.quickActions')}
        </AppText>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.attendance')}
            icon="clipboard"
            colorVariant="coral"
          />
          <DashboardButton
            label={t('dashboard.events')}
            icon="calendar"
            colorVariant="orange"
          />
        </View>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.reports')}
            icon="bar-chart"
            colorVariant="yellow"
          />
          <DashboardButton
            label={t('dashboard.announcements')}
            icon="megaphone"
            colorVariant="teal"
          />
        </View>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.mealMenus')}
            icon="restaurant"
            colorVariant="coral"
            onPress={() => router.push('/manage/meal-menus')}
          />
        </View>
      </View>

      {/* My Classes */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.myClasses')}
        </AppText>
        {classes && classes.length > 0 ? (
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
              </View>
            </InfoCard>
          ))
        ) : (
          <InfoCard title={t('dashboard.noClasses')} />
        )}
      </View>

      {/* My Students */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.myStudents')}
        </AppText>
        {students && students.length > 0 ? (
          students.slice(0, 5).map((student) => (
            <InfoCard
              key={student.student_id}
              title={`${student.first_name} ${student.last_name}`}
              subtitle={student.date_of_birth ? `${t('student.dateOfBirth')}: ${student.date_of_birth}` : undefined}
            >
              {student.student_allergies && student.student_allergies.length > 0 && (
                <View style={styles.allergyContainer}>
                  <Icon name="warning" size={14} color={BrandColors.coral} />
                  <AppText variant="caption" color={BrandColors.coral} style={{ marginLeft: 4 }}>
                    {student.student_allergies.map(a => a.allergy_name).join(', ')}
                  </AppText>
                </View>
              )}
            </InfoCard>
          ))
        ) : (
          <InfoCard title={t('dashboard.noStudents')} />
        )}
        {students && students.length > 5 && (
          <DashboardButton
            label={t('dashboard.viewAll')}
            colorVariant="teal"
          />
        )}
      </View>
    </View>
  );
}
