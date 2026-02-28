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
import { useListClassesQuery } from '@/store/api/classApi';

export default function ClassesManagementScreen() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const { data: classesData, isLoading } = useListClassesQuery({ pageSize: 100 });
  const classes = classesData?.data || [];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: theme.background }]} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Button label={t('common.back')} onPress={() => router.back()} variant="ghost" style={styles.backButton} />
        <AppText variant="heading" style={styles.headerTitle}>{t('dashboard.manageClasses')}</AppText>
        <View style={{ width: 60 }} />
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        {isLoading ? (
          <View style={{ gap: 12 }}>
            <Skeleton width="100%" height={80} borderRadius={16} />
          </View>
        ) : classes.length > 0 ? (
          classes.map((cls) => (
            <InfoCard key={cls.class_id} title={cls.class_name} subtitle={`${t('class.room')}: ${cls.room_number || 'N/A'}`} />
          ))
        ) : (
          <AppText variant="body" color={theme.textSecondary}>No classes found.</AppText>
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
