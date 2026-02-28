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
import { useListParentsQuery } from '@/store/api/parentApi';

export default function ParentsManagementScreen() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const { data: parentsData, isLoading } = useListParentsQuery({ pageSize: 100 });

  const parents = parentsData?.data || [];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: theme.background }]} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Button label={t('common.back')} onPress={() => router.back()} variant="ghost" style={styles.backButton} />
        <AppText variant="heading" style={styles.headerTitle}>
          {t('dashboard.manageParents')}
        </AppText>
        <View style={{ width: 60 }} />
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        {isLoading ? (
          <View style={{ gap: 12 }}>
            <Skeleton width="100%" height={80} borderRadius={16} />
            <Skeleton width="100%" height={80} borderRadius={16} />
          </View>
        ) : parents.length > 0 ? (
          parents.map((parent) => (
            <InfoCard
              key={parent.user_id}
              title={`${parent.first_name} ${parent.last_name}`}
              subtitle={parent.email}
            />
          ))
        ) : (
          <AppText variant="body" color={theme.textSecondary}>
            No parents found.
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
