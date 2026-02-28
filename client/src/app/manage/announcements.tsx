import { useRouter } from 'expo-router';
import React from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppText } from '@/components/atoms/AppText';
import { Button } from '@/components/atoms/Button';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';

export default function AnnouncementsScreen() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: theme.background }]} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Button label={t('common.back')} onPress={() => router.back()} variant="ghost" style={styles.backButton} />
        <AppText variant="heading" style={styles.headerTitle}>{t('dashboard.announcements')}</AppText>
        <View style={{ width: 60 }} />
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        <AppText variant="body" color={theme.textSecondary}>Announcements coming soon...</AppText>
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
