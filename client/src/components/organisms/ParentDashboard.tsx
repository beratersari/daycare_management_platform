/**
 * Organism — ParentDashboard
 * Dashboard view for parent users showing their children's information.
 * Uses DraggableFlatList for reordering children.
 */
import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import DraggableFlatList, { ScaleDecorator, RenderItemParams } from 'react-native-draggable-flatlist';

import { AppText } from '@/components/atoms/AppText';
import { Skeleton } from '@/components/atoms/Skeleton';
import { InfoCard } from '@/components/molecules/InfoCard';
import { DashboardButton } from '@/components/molecules/DashboardButton';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useGetMyChildrenQuery } from '@/store/api/parentApi';
import { useGetClassQuery } from '@/store/api/classApi';
import type { StudentResponse } from '@/store/api/studentApi';
import { BrandColors } from '@/constants/theme';

export function ParentDashboard() {
  const theme = useTheme();
  const { t } = useLocalization();
  const router = useRouter();
  const { data: childrenData, isLoading, error } = useGetMyChildrenQuery();
  const [data, setData] = useState<StudentResponse[]>([]);

  useEffect(() => {
    if (childrenData) {
      setData([...childrenData]);
    }
  }, [childrenData]);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <View style={styles.headerContainer}>
          <Skeleton width="100%" height={150} borderRadius={16} />
          <Skeleton width={150} height={20} />
        </View>
        <View style={{ gap: 12, marginTop: 12 }}>
          <Skeleton width="100%" height={120} borderRadius={16} />
          <Skeleton width="100%" height={120} borderRadius={16} />
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.loadingContainer}>
        <AppText variant="body" color={theme.textSecondary}>
          {t('common.error')}
        </AppText>
      </View>
    );
  }

  const renderItem = ({ item, drag, isActive }: RenderItemParams<StudentResponse>) => {
    return (
      <ScaleDecorator>
        <Pressable
          onLongPress={drag}
          disabled={isActive}
          onPress={() => router.push(`/student/${item.student_id}`)}
          style={({ pressed }) => [
            isActive ? styles.activeItem : undefined,
            pressed ? styles.pressedItem : undefined,
          ]}
        >
          <ChildCard child={item} />
        </Pressable>
      </ScaleDecorator>
    );
  };

  const ListHeader = () => (
    <View style={styles.headerContainer}>
      {/* Quick Actions */}
      <View style={styles.section}>
        <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
          {t('dashboard.quickActions')}
        </AppText>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.attendance')}
            icon="📅"
            colorVariant="coral"
          />
          <DashboardButton
            label={t('dashboard.events')}
            icon="🎉"
            colorVariant="orange"
          />
        </View>
        <View style={styles.buttonRow}>
          <DashboardButton
            label={t('dashboard.mealMenus')}
            icon="🍽️"
            colorVariant="yellow"
            onPress={() => router.push('/manage/meal-menus')}
          />
          <DashboardButton
            label={t('dashboard.announcements')}
            icon="📢"
            colorVariant="teal"
          />
        </View>
      </View>

      <AppText variant="label" color={theme.textSecondary} style={styles.sectionLabel}>
        {t('dashboard.myChildren')} (Long press to reorder)
      </AppText>
    </View>
  );

  return (
    <View style={styles.container}>
      <DraggableFlatList
        data={data}
        onDragEnd={({ data }) => setData(data)}
        keyExtractor={(item) => item.student_id.toString()}
        renderItem={renderItem}
        ListHeaderComponent={ListHeader}
        ListEmptyComponent={<InfoCard title={t('dashboard.noChildren')} />}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

function ClassInfoRow({ classId }: { classId: number }) {
  const theme = useTheme();
  const { t } = useLocalization();
  const { data: cls, isLoading } = useGetClassQuery(classId);

  if (isLoading) {
    return <Skeleton width={150} height={16} style={{ marginTop: 4 }} />;
  }

  if (!cls) return null;

  return (
    <AppText variant="caption" color={theme.textSecondary}>
      🏫 {cls.class_name} ({t('class.room')}: {cls.room_number || 'N/A'})
    </AppText>
  );
}

function ChildCard({ child }: { child: StudentResponse }) {
  const theme = useTheme();
  const { t } = useLocalization();

  return (
    <InfoCard
      title={`${child.first_name} ${child.last_name}`}
      subtitle={child.date_of_birth ? `${t('student.dateOfBirth')}: ${child.date_of_birth}` : undefined}
    >
      <View style={styles.childDetails}>
        {child.student_allergies && child.student_allergies.length > 0 && (
          <View style={styles.allergyContainer}>
            <AppText variant="caption" color={theme.textSecondary}>
              {t('student.allergies')}:
            </AppText>
            <AppText variant="caption" color={BrandColors.coral}>
              {' '}{child.student_allergies.map(a => a.allergy_name).join(', ')}
            </AppText>
          </View>
        )}
        {child.class_ids && child.class_ids.length > 0 && (
          <View style={{ gap: 2 }}>
            {child.class_ids.map((id) => (
              <ClassInfoRow key={id} classId={id} />
            ))}
          </View>
        )}
      </View>
    </InfoCard>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listContent: {
    paddingBottom: 24,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 32,
  },
  headerContainer: {
    gap: 16,
    marginBottom: 8,
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
  buttonRow: {
    flexDirection: 'row',
    gap: 10,
  },
  childDetails: {
    marginTop: 8,
    gap: 4,
  },
  allergyContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  activeItem: {
    opacity: 0.7,
  },
  pressedItem: {
    opacity: 0.9,
  },
});
