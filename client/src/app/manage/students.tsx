import { useRouter } from 'expo-router';
import React from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { AppText } from '@/components/atoms/AppText';
import { Button } from '@/components/atoms/Button';
import { Skeleton } from '@/components/atoms/Skeleton';
import { InfoCard } from '@/components/molecules/InfoCard';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useListStudentsQuery } from '@/store/api/studentApi';

export default function StudentsManagementScreen() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const { data: studentsData, isLoading } = useListStudentsQuery({ pageSize: 100 });

  const students = studentsData?.data || [];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: theme.background }]} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Button label={t('common.back')} onPress={() => router.back()} variant="ghost" style={styles.backButton} />
        <AppText variant="heading" style={styles.headerTitle}>
          {t('dashboard.manageStudents')}
        </AppText>
        <View style={{ width: 60 }} />
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        {isLoading ? (
          <View style={{ gap: 12 }}>
            <Skeleton width="100%" height={80} borderRadius={16} />
            <Skeleton width="100%" height={80} borderRadius={16} />
          </View>
        ) : students.length > 0 ? (
          students.map((student) => (
            <InfoCard
              key={student.student_id}
              title={`${student.first_name} ${student.last_name}`}
              subtitle={student.date_of_birth ? `${t('student.dateOfBirth')}: ${student.date_of_birth}` : undefined}
              onPress={() => router.push(`/student/${student.student_id}`)}
            />
          ))
        ) : (
          <AppText variant="body" color={theme.textSecondary}>
            No students found.
          </AppText>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12 },
  backButton: { height: 40, width: 60, paddingHorizontal: 0 },
  headerTitle: { textAlign: 'center' },
  content: { padding: 24, gap: 12 },
});
