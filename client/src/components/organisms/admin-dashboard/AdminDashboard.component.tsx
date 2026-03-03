/**
 * Organism — AdminDashboard
 *
 * Enhanced dashboard view for admin and director users with improved structure,
 * organized sections, and quick-add functionality.
 *
 * Features:
 * - School selector with visual cards
 * - Quick Actions section with prominent "Add Student" button
 * - Organized Management Tools grid
 * - Recent Activity feed
 * - Overview Statistics with visual indicators
 * - Quick Access shortcuts
 */
import { useRouter } from 'expo-router';
import React, { useEffect, useMemo, useState } from 'react';
import { Pressable, View, ScrollView } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { Icon } from '@/components/atoms/icon';
import { DashboardButton, ButtonColorVariant } from '@/components/molecules/dashboard-button';
import { InfoCard } from '@/components/molecules/info-card';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useListTeachersQuery } from '@/store/api/teacherApi';
import { useListStudentsQuery } from '@/store/api/studentApi';
import { useListClassesQuery } from '@/store/api/classApi';
import { useListParentsQuery } from '@/store/api/parentApi';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { useGetActiveTermBySchoolQuery } from '@/store/api/termApi';
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
  /** Optional icon name */
  icon?: string;
  /** Press handler for the card */
  onPress?: () => void;
}

/**
 * Enhanced Stat Card with icon and press capability
 */
function StatCard({ label, value, color, icon, onPress }: StatCardProps) {
  const theme = useTheme();

  const cardContent = (
    <View style={[styles.statCard, { backgroundColor: theme.backgroundElement }]}>
      <View style={styles.statHeader}>
        {icon && (
          <View style={[styles.statIconContainer, { backgroundColor: STAT_COLORS[color] + '20' }]}>
            <Icon name={icon} size={20} color={STAT_COLORS[color]} />
          </View>
        )}
        <AppText variant="display" color={STAT_COLORS[color]} style={styles.statValue}>
          {value}
        </AppText>
      </View>
      <AppText variant="caption" color={theme.textSecondary} style={styles.statLabel}>
        {label}
      </AppText>
    </View>
  );

  if (onPress) {
    return (
      <Pressable onPress={onPress} style={styles.statCardPressable}>
        {cardContent}
      </Pressable>
    );
  }

  return cardContent;
}

/**
 * Quick Action Card for prominent actions
 */
function QuickActionCard({
  label,
  icon,
  color,
  onPress,
  description,
}: {
  label: string;
  icon: string;
  color: string;
  onPress: () => void;
  description?: string;
}) {
  const theme = useTheme();

  return (
    <Pressable
      onPress={onPress}
      style={[styles.quickActionCard, { backgroundColor: color + '15' }]}
    >
      <View style={[styles.quickActionIconContainer, { backgroundColor: color }]}>
        <Icon name={icon} size={24} color="#fff" />
      </View>
      <View style={styles.quickActionTextContainer}>
        <AppText variant="body" style={styles.quickActionLabel}>
          {label}
        </AppText>
        {description && (
          <AppText variant="caption" color={theme.textSecondary}>
            {description}
          </AppText>
        )}
      </View>
      <Icon name="chevron-forward" size={20} color={color} />
    </Pressable>
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

  const { data: activeTerm } = useGetActiveTermBySchoolQuery(selectedSchoolId || 0, {
    skip: !selectedSchoolId,
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

  // Calculate capacity utilization
  const totalCapacity = classesData?.data?.reduce((sum, cls) => sum + (cls.capacity || 0), 0) || 0;
  const totalStudents = studentsData?.total || 0;
  const capacityUtilization = totalCapacity > 0 ? Math.round((totalStudents / totalCapacity) * 100) : 0;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* School Selection Section */}
      {(userRole === 'ADMIN' || userRole === 'DIRECTOR') && selectedSchool ? (
        <View style={styles.section}>
          <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
            {t('dashboard.managingSchool')}
          </AppText>
          {userRole === 'ADMIN' && schools && schools.length > 0 ? (
            <View style={styles.schoolSelectorContainer}>
              {schools.map((school) => (
                <Pressable
                  key={school.school_id}
                  onPress={() => setSelectedSchoolId(school.school_id)}
                  style={[
                    styles.schoolCard,
                    selectedSchoolId === school.school_id && styles.schoolCardSelected,
                    { backgroundColor: theme.backgroundElement },
                  ]}
                >
                  <View style={styles.schoolCardHeader}>
                    <View style={[styles.schoolIcon, { backgroundColor: selectedSchoolId === school.school_id ? BrandColors.coral : BrandColors.teal }]}>
                      <Icon name="school" size={20} color="#fff" />
                    </View>
                    <AppText
                      variant="body"
                      style={styles.schoolCardName}
                      color={selectedSchoolId === school.school_id ? BrandColors.coral : theme.text}
                    >
                      {school.school_name}
                    </AppText>
                  </View>
                  {school.address && (
                    <AppText variant="caption" color={theme.textSecondary} numberOfLines={1}>
                      {school.address}
                    </AppText>
                  )}
                </Pressable>
              ))}
            </View>
          ) : (
            <View style={[styles.selectedSchoolCard, { backgroundColor: theme.backgroundElement }]}>
              <View style={styles.schoolCardHeader}>
                <View style={[styles.schoolIcon, { backgroundColor: BrandColors.teal }]}>
                  <Icon name="school" size={24} color="#fff" />
                </View>
                <View style={styles.schoolInfo}>
                  <AppText variant="subheading">{selectedSchool.school_name}</AppText>
                  {selectedSchool.address ? (
                    <AppText variant="caption" color={theme.textSecondary}>
                      {selectedSchool.address}
                    </AppText>
                  ) : null}
                </View>
              </View>
            </View>
          )}

          {/* Active Term Indicator */}
          {activeTerm && (
            <View style={[styles.activeTermBanner, { backgroundColor: BrandColors.teal + '15' }]}>
              <Icon name="calendar" size={18} color={BrandColors.teal} />
              <AppText variant="body" style={styles.activeTermText}>
                Active Term: <AppText variant="body" style={{ fontWeight: '600' }}>{activeTerm.term_name}</AppText>
              </AppText>
            </View>
          )}
        </View>
      ) : null}

      {/* Quick Actions Section - Quick Add Buttons */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          Quick Add
        </AppText>
        <View style={styles.quickAddGrid}>
          <QuickActionCard
            label="Add Student"
            icon="person-add"
            color={BrandColors.coral}
            description="Enroll new student"
            onPress={() => router.push('/manage/students/add')}
          />
          <QuickActionCard
            label="Add Teacher"
            icon="school"
            color={BrandColors.teal}
            description="Add new teacher"
            onPress={() => router.push('/manage/teachers/add')}
          />
          <QuickActionCard
            label="Add Class"
            icon="library"
            color={BrandColors.yellow}
            description="Create new class"
            onPress={() => router.push('/manage/classes/add')}
          />
          <QuickActionCard
            label="Add Parent"
            icon="people"
            color={BrandColors.orange}
            description="Add new parent"
            onPress={() => router.push('/manage/parents/add')}
          />
        </View>
      </View>

      {/* Overview Statistics */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          Overview
        </AppText>
        <View style={styles.statsGrid}>
          <StatCard
            label="Teachers"
            value={getStatValue(teachersData?.total)}
            color="coral"
            icon="school"
            onPress={() => router.push('/manage/teachers')}
          />
          <StatCard
            label="Students"
            value={getStatValue(studentsData?.total)}
            color="orange"
            icon="happy"
            onPress={() => router.push('/manage/students')}
          />
          <StatCard
            label="Classes"
            value={getStatValue(classesData?.total)}
            color="yellow"
            icon="library"
            onPress={() => router.push('/manage/classes')}
          />
          <StatCard
            label="Parents"
            value={getStatValue(parentsData?.total)}
            color="teal"
            icon="people"
            onPress={() => router.push('/manage/parents')}
          />
        </View>

        {/* Capacity Utilization */}
        {totalCapacity > 0 && (
          <InfoCard title="Capacity Utilization" noPadding>
            <View style={styles.capacityContainer}>
              <View style={styles.capacityHeader}>
                <AppText variant="body" style={styles.capacityText}>
                  {totalStudents} of {totalCapacity} spots filled
                </AppText>
                <AppText
                  variant="body"
                  color={capacityUtilization > 90 ? BrandColors.coral : capacityUtilization > 70 ? BrandColors.orange : BrandColors.teal}
                  style={styles.capacityPercentage}
                >
                  {capacityUtilization}%
                </AppText>
              </View>
              <View style={styles.capacityBarContainer}>
                <View
                  style={[
                    styles.capacityBar,
                    {
                      width: `${Math.min(capacityUtilization, 100)}%`,
                      backgroundColor: capacityUtilization > 90 ? BrandColors.coral : capacityUtilization > 70 ? BrandColors.orange : BrandColors.teal,
                    },
                  ]}
                />
              </View>
            </View>
          </InfoCard>
        )}
      </View>

      {/* Management Tools Section - Combined Manage & Add */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.managementTools')}
        </AppText>
        
        {/* Students Row */}
        <View style={styles.manageRow}>
          <DashboardButton
            label={t('dashboard.manageStudents')}
            icon="happy"
            colorVariant="coral"
            onPress={() => router.push('/manage/students')}
            style={styles.manageButton}
          />
          <Pressable
            onPress={() => router.push('/manage/students/add')}
            style={[styles.addButton, { backgroundColor: BrandColors.coral }]}
          >
            <Icon name="add" size={24} color="#fff" />
          </Pressable>
        </View>
        
        {/* Teachers Row */}
        <View style={styles.manageRow}>
          <DashboardButton
            label={t('dashboard.manageTeachers')}
            icon="school"
            colorVariant="teal"
            onPress={() => router.push('/manage/teachers')}
            style={styles.manageButton}
          />
          <Pressable
            onPress={() => router.push('/manage/teachers/add')}
            style={[styles.addButton, { backgroundColor: BrandColors.teal }]}
          >
            <Icon name="add" size={24} color="#fff" />
          </Pressable>
        </View>
        
        {/* Classes Row */}
        <View style={styles.manageRow}>
          <DashboardButton
            label={t('dashboard.manageClasses')}
            icon="library"
            colorVariant="yellow"
            onPress={() => router.push('/manage/classes')}
            style={styles.manageButton}
          />
          <Pressable
            onPress={() => router.push('/manage/classes/add')}
            style={[styles.addButton, { backgroundColor: BrandColors.yellow }]}
          >
            <Icon name="add" size={24} color="#fff" />
          </Pressable>
        </View>
        
        {/* Parents Row */}
        <View style={styles.manageRow}>
          <DashboardButton
            label={t('dashboard.manageParents')}
            icon="people"
            colorVariant="orange"
            onPress={() => router.push('/manage/parents')}
            style={styles.manageButton}
          />
          <Pressable
            onPress={() => router.push('/manage/parents/add')}
            style={[styles.addButton, { backgroundColor: BrandColors.orange }]}
          >
            <Icon name="add" size={24} color="#fff" />
          </Pressable>
        </View>
        
        {/* Other Tools Grid */}
        <View style={styles.toolsGrid}>
          <DashboardButton
            label={t('dashboard.manageTerms')}
            icon="calendar"
            colorVariant="coral"
            onPress={() => router.push('/manage/terms')}
          />
          <DashboardButton
            label={t('dashboard.announcements')}
            icon="megaphone"
            colorVariant="orange"
            onPress={() => router.push('/manage/announcements')}
          />
        </View>
      </View>

      {/* Additional Tools */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          Operations
        </AppText>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.reports')}
            icon="bar-chart"
            colorVariant="coral"
            onPress={() => router.push('/manage/reports')}
          />
          <DashboardButton
            label={t('dashboard.events')}
            icon="calendar"
            colorVariant="yellow"
            onPress={() => router.push('/manage/events')}
          />
        </View>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.mealMenus')}
            icon="restaurant"
            colorVariant="teal"
            onPress={() => router.push('/manage/meal-menus')}
          />
          <DashboardButton
            label="Attendance"
            icon="checkbox"
            colorVariant="orange"
            onPress={() => router.push('/manage/attendance')}
          />
        </View>
      </View>
    </ScrollView>
  );
}
