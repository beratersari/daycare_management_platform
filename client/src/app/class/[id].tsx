/**
 * Class Detail Screen with Assignment Management
 *
 * Displays detailed information about a class and allows
 * role-based management of student and teacher assignments.
 *
 * Roles:
 * - ADMIN/DIRECTOR: Full management (add/remove students and teachers)
 * - TEACHER: View assignments, limited management
 * - PARENT: View-only access to their child's class
 */
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useState } from 'react';
import { StyleSheet, View, ScrollView, Pressable } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { Icon } from '@/components/atoms/icon';
import { PageHeader } from '@/components/molecules/page-header';
import { InfoCard } from '@/components/molecules/info-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { ClassAssignments } from '@/components/organisms/class-assignments';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { useGetClassQuery, useGetClassAssignmentsQuery } from '@/store/api/classApi';
import { BrandColors } from '@/constants/theme';

export default function ClassDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const user = useAppSelector(selectCurrentUser);

  const classId = typeof id === 'string' ? parseInt(id, 10) : 0;
  const [error, setError] = useState<string | null>(null);

  // Queries
  const { data: classData, isLoading: isLoadingClass } = useGetClassQuery(classId, {
    skip: !classId,
  });
  const { data: assignments, isLoading: isLoadingAssignments, refetch } = useGetClassAssignmentsQuery(
    { classId },
    { skip: !classId }
  );

  // Permissions
  const userRole = user?.role;
  const canManageAssignments = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  const canViewAssignments = true;

  const isLoading = isLoadingClass || isLoadingAssignments;

  // Handle refresh
  const handleAssignmentsChange = () => {
    refetch();
  };

  if (isLoading) {
    return (
      <ScreenTemplate
        scrollable={false}
        header={
          <PageHeader
            title={t('class.classDetails')}
            onBack={() => router.back()}
          />
        }>
        <LoadingState cardCount={3} />
      </ScreenTemplate>
    );
  }

  if (!classData) {
    return (
      <ScreenTemplate
        scrollable={false}
        header={
          <PageHeader
            title={t('class.classDetails')}
            onBack={() => router.back()}
          />
        }>
        <EmptyState
          icon="🏫"
          message={t('class.notFound')}
          subtitle={t('class.notFoundSubtitle')}
        />
        <Button
          label={t('common.back')}
          onPress={() => router.back()}
          variant="secondary"
          style={{ marginTop: 16 }}
        />
      </ScreenTemplate>
    );
  }

  const capacityPercentage = assignments?.capacity
    ? ((assignments.current_student_count || 0) / assignments.capacity) * 100
    : 0;
  const isNearCapacity = capacityPercentage >= 80 && capacityPercentage < 100;
  const isAtCapacity = assignments?.capacity !== null && assignments?.capacity !== undefined && 
    (assignments?.current_student_count || 0) >= assignments.capacity;

  return (
    <ScreenTemplate
      scrollable={true}
      header={
        <PageHeader
          title={classData.class_name}
          onBack={() => router.back()}
          rightElement={
            canManageAssignments ? (
              <Button
                label="Edit"
                variant="ghost"
                onPress={() => router.push(`/manage/classes?edit=${classId}`)}
              />
            ) : null
          }
        />
      }>
      {/* Error Banner */}
      {error && (
        <AlertBanner
          type="error"
          message={error}
          onDismiss={() => setError(null)}
        />
      )}

      {/* Class Info Card */}
      <InfoCard
        title={t('class.info')}
        rightElement={
          assignments?.term_name ? (
            <View style={styles.termBadge}>
              <AppText variant="caption" color="#fff">
                {assignments.term_name}
              </AppText>
            </View>
          ) : null
        }
      >
        {/* Capacity Section */}
        <View style={styles.capacityContainer}>
          <View style={styles.capacityHeader}>
            <AppText variant="label" color={theme.textSecondary}>
              {t('class.capacity')}
            </AppText>
            <AppText variant="body" style={{ fontWeight: '600' }}>
              {assignments?.capacity !== null && assignments?.capacity !== undefined
                ? `${assignments.current_student_count}/${assignments.capacity}`
                : `${assignments?.current_student_count || 0} students`}
            </AppText>
          </View>
          
          {/* Capacity Bar */}
          {assignments?.capacity !== null && assignments?.capacity !== undefined && (
            <>
              <View style={styles.capacityBar}>
                <View
                  style={[
                    styles.capacityFill,
                    {
                      width: `${Math.min(capacityPercentage, 100)}%`,
                      backgroundColor: isAtCapacity
                        ? '#dc2626'
                        : isNearCapacity
                        ? '#f59e0b'
                        : '#22c55e',
                    },
                  ]}
                />
              </View>
              
              {/* Capacity Status */}
              <View style={styles.capacityStatus}>
                {isAtCapacity ? (
                  <View style={styles.statusBadgeFull}>
                    <Icon name="warning" size={14} color="#fff" />
                    <AppText variant="caption" color="#fff">
                      At Capacity
                    </AppText>
                  </View>
                ) : isNearCapacity ? (
                  <View style={styles.statusBadgeNear}>
                    <Icon name="alert-circle" size={14} color="#92400e" />
                    <AppText variant="caption" color="#92400e">
                      Almost Full
                    </AppText>
                  </View>
                ) : (
                  <View style={styles.statusBadgeAvailable}>
                    <Icon name="checkmark-circle" size={14} color="#166534" />
                    <AppText variant="caption" color="#166534">
                      {assignments.available_spots} spots available
                    </AppText>
                  </View>
                )}
              </View>
            </>
          )}
        </View>

        {/* Quick Stats */}
        <View style={styles.statsGrid}>
          <View style={[styles.statItem, { backgroundColor: '#fef2f2' }]}>
            <Icon name="people" size={20} color={BrandColors.coral} />
            <AppText variant="display" color={BrandColors.coral}>
              {assignments?.students.length || 0}
            </AppText>
            <AppText variant="caption" color={theme.textSecondary}>
              Students
            </AppText>
          </View>
          
          <View style={[styles.statItem, { backgroundColor: '#f0fdf4' }]}>
            <Icon name="school" size={20} color={BrandColors.teal} />
            <AppText variant="display" color={BrandColors.teal}>
              {assignments?.teachers.length || 0}
            </AppText>
            <AppText variant="caption" color={theme.textSecondary}>
              Teachers
            </AppText>
          </View>
        </View>
      </InfoCard>

      {/* Role-based Info Banner */}
      {canManageAssignments && (
        <View style={styles.infoBanner}>
          <Icon name="information-circle" size={20} color={BrandColors.coral} />
          <AppText variant="body" style={{ flex: 1 }}>
            As an {userRole?.toLowerCase()}, you can add or remove students and teachers from this class.
          </AppText>
        </View>
      )}
      
      {userRole === 'TEACHER' && (
        <View style={styles.infoBanner}>
          <Icon name="information-circle" size={20} color={BrandColors.teal} />
          <AppText variant="body" style={{ flex: 1 }}>
            You can view all students and teachers assigned to this class.
          </AppText>
        </View>
      )}

      {/* Assignment Management */}
      {canViewAssignments && (
        <InfoCard title="Assignments" noPadding>
          <ClassAssignments
            classId={classId}
            className={classData.class_name}
            onAssignmentsChange={handleAssignmentsChange}
          />
        </InfoCard>
      )}
    </ScreenTemplate>
  );
}

const styles = StyleSheet.create({
  // Capacity Styles
  capacityContainer: {
    gap: 8,
    marginBottom: 16,
  },
  capacityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  capacityBar: {
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  capacityFill: {
    height: '100%',
    borderRadius: 4,
  },
  capacityStatus: {
    flexDirection: 'row',
    marginTop: 4,
  },
  statusBadgeFull: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#dc2626',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeNear: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#fef3c7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeAvailable: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#dcfce7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  
  // Term Badge
  termBadge: {
    backgroundColor: BrandColors.coral,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  
  // Stats Grid
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 4,
  },
  
  // Info Banner
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    marginVertical: 8,
  },
});
