/**
 * Student Detail Screen
 *
 * Displays detailed information about a student.
 * Editable for Teachers/Admins, Read-only for Parents.
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses InfoCard molecules for information sections
 * - Uses ProfileLoadingState for loading UX
 */
import { useLocalSearchParams, useRouter } from 'expo-router';
import React from 'react';
import { StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { PageHeader } from '@/components/molecules/page-header';
import { InfoCard } from '@/components/molecules/info-card';
import { ProfileLoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useGetStudentQuery } from '@/store/api/studentApi';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { BrandColors } from '@/constants/theme';

export default function StudentDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const user = useAppSelector(selectCurrentUser);
  
  const studentId = typeof id === 'string' ? parseInt(id, 10) : 0;
  const { data: student, isLoading, error } = useGetStudentQuery(studentId, {
    skip: !studentId,
  });

  const canEdit = user?.role === 'TEACHER' || user?.role === 'ADMIN' || user?.role === 'DIRECTOR';

  if (isLoading) {
    return (
      <ScreenTemplate
        scrollable={true}
        header={
          <PageHeader
            title={t('dashboard.studentInfo')}
            onBack={() => router.back()}
          />
        }>
        <ProfileLoadingState showAvatar={true} />
      </ScreenTemplate>
    );
  }

  if (error || !student) {
    return (
      <ScreenTemplate
        scrollable={false}
        header={
          <PageHeader
            title={t('dashboard.studentInfo')}
            onBack={() => router.back()}
          />
        }>
        <EmptyState
          icon="❌"
          message={t('common.error')}
          subtitle="Unable to load student information"
        />
        <Button
          label={t('common.back')}
          onPress={() => router.back()}
          variant="secondary"
        />
      </ScreenTemplate>
    );
  }

  return (
    <ScreenTemplate
      scrollable={true}
      header={
        <PageHeader
          title={t('dashboard.studentInfo')}
          onBack={() => router.back()}
        />
      }>
      {/* Profile Header */}
      <View style={styles.profileHeader}>
        <View style={styles.avatarPlaceholder}>
          <AppText variant="display" color="#fff">
            {student.first_name[0]}{student.last_name[0]}
          </AppText>
        </View>
        <AppText variant="heading">
          {student.first_name} {student.last_name}
        </AppText>
        <AppText variant="body" color={theme.textSecondary}>
          {t('student.dateOfBirth')}: {student.date_of_birth || 'N/A'}
        </AppText>
      </View>

      {/* Allergies Section */}
      <InfoCard 
        title={t('student.allergies')} 
        rightElement={canEdit ? (
          <Button label={t('common.edit')} variant="ghost" style={{ height: 32, paddingHorizontal: 8 }} />
        ) : null}
      >
        {student.student_allergies && student.student_allergies.length > 0 ? (
          student.student_allergies.map((allergy) => (
            <View key={allergy.allergy_id} style={styles.allergyItem}>
              <AppText variant="body" style={{ fontWeight: '600', color: BrandColors.coral }}>
                {allergy.allergy_name}
              </AppText>
              {allergy.severity && (
                <AppText variant="caption" color={theme.textSecondary}>
                  Severity: {allergy.severity}
                </AppText>
              )}
              {allergy.notes && (
                <AppText variant="caption" color={theme.textSecondary}>
                  Note: {allergy.notes}
                </AppText>
              )}
            </View>
          ))
        ) : (
          <AppText variant="body" color={theme.textSecondary}>
            {t('student.noAllergies')}
          </AppText>
        )}
      </InfoCard>

      {/* Medical Info Section */}
      <InfoCard 
        title={t('student.medicalInfo')}
        rightElement={canEdit ? (
          <Button label={t('common.edit')} variant="ghost" style={{ height: 32, paddingHorizontal: 8 }} />
        ) : null}
      >
        {student.student_hw_info && student.student_hw_info.length > 0 ? (
          student.student_hw_info.map((info) => (
            <View key={info.hw_id} style={styles.hwItem}>
              <AppText variant="caption" color={theme.textSecondary}>
                {info.measurement_date}
              </AppText>
              <View style={styles.hwRow}>
                <AppText variant="body">Height: {info.height} cm</AppText>
                <AppText variant="body">Weight: {info.weight} kg</AppText>
              </View>
            </View>
          ))
        ) : (
          <AppText variant="body" color={theme.textSecondary}>
            No measurements recorded
          </AppText>
        )}
      </InfoCard>

      {/* Emergency Contact */}
      <InfoCard title={t('student.emergencyContact')}>
        <AppText variant="body">
          {student.parents && student.parents.length > 0 ? "Parents linked" : "No parents linked"}
        </AppText>
      </InfoCard>
    </ScreenTemplate>
  );
}

const styles = StyleSheet.create({
  profileHeader: {
    alignItems: 'center',
    gap: 8,
    marginBottom: 16,
  },
  avatarPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: BrandColors.teal,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  allergyItem: {
    marginBottom: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  hwItem: {
    marginBottom: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  hwRow: {
    flexDirection: 'row',
    gap: 16,
  },
});
