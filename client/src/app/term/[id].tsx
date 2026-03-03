/**
 * Term Detail Screen with Class Assignment Management
 *
 * Displays detailed information about a term and allows
 * admins/directors to manage class assignments.
 *
 * Roles:
 * - ADMIN/DIRECTOR: Full management (assign/remove classes)
 * - TEACHER: View-only access
 */
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useState, useMemo, useCallback } from 'react';
import { View, ScrollView, Pressable, Modal, TextInput, ActivityIndicator, StyleSheet } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { Icon } from '@/components/atoms/icon';
import { PageHeader } from '@/components/molecules/page-header';
import { InfoCard } from '@/components/molecules/info-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import {
  useGetTermQuery,
  useGetClassesByTermQuery,
  useAssignClassToTermMutation,
  useUnassignClassFromTermMutation,
} from '@/store/api/termApi';
import { useListClassesQuery, type ClassResponse } from '@/store/api/classApi';
import { BrandColors } from '@/constants/theme';

// Helper function to format date
const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return 'Ongoing';
  return dateStr.split('T')[0];
};

// Helper to check if term is active
const isTermActive = (term: { activity_status: boolean; end_date?: string | null }) => {
  if (!term.activity_status) return false;
  if (term.end_date && new Date(term.end_date) < new Date()) return false;
  return true;
};

export default function TermDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const user = useAppSelector(selectCurrentUser);

  const termId = typeof id === 'string' ? parseInt(id, 10) : 0;
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Queries
  const { data: term, isLoading: isLoadingTerm } = useGetTermQuery(termId, {
    skip: !termId,
  });
  const { data: termClasses, isLoading: isLoadingClasses, refetch: refetchClasses } = useGetClassesByTermQuery(termId, {
    skip: !termId,
  });
  const { data: allClasses, isLoading: isLoadingAllClasses } = useListClassesQuery({ pageSize: 100 }, {
    skip: !showAddModal,
  });

  // Mutations
  const [assignClass, { isLoading: isAssigning }] = useAssignClassToTermMutation();
  const [unassignClass, { isLoading: isUnassigning }] = useUnassignClassFromTermMutation();

  // Permissions
  const userRole = user?.role;
  const canManage = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  const termIsActive = term ? isTermActive(term) : false;

  // Derived data
  const assignedClassIds = useMemo(
    () => new Set(termClasses?.map((c) => c.class_id) || []),
    [termClasses]
  );

  const filteredClasses = useMemo(() => {
    if (!allClasses?.data) return [];
    // Filter by school if term has school_id
    const schoolClasses = term?.school_id
      ? allClasses.data.filter((c) => c.school_id === term.school_id)
      : allClasses.data;
    return schoolClasses.filter((c) =>
      c.class_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [allClasses, term?.school_id, searchQuery]);

  // Handlers
  const handleAssignClass = useCallback(
    async (classId: number) => {
      try {
        await assignClass({ classId, termId }).unwrap();
        refetchClasses();
      } catch (err) {
        setError(t('terms.assignFailed'));
      }
    },
    [assignClass, termId, refetchClasses, t]
  );

  const handleUnassignClass = useCallback(
    async (classId: number) => {
      try {
        await unassignClass({ classId, termId }).unwrap();
        refetchClasses();
      } catch (err) {
        setError(t('terms.assignFailed'));
      }
    },
    [unassignClass, termId, refetchClasses, t]
  );

  const isLoading = isLoadingTerm || isLoadingClasses;
  const isMutating = isAssigning || isUnassigning;

  if (isLoading) {
    return (
      <ScreenTemplate
        scrollable={false}
        header={<PageHeader title="Term Details" onBack={() => router.back()} />}
      >
        <LoadingState cardCount={3} />
      </ScreenTemplate>
    );
  }

  if (!term) {
    return (
      <ScreenTemplate
        scrollable={false}
        header={<PageHeader title="Term Not Found" onBack={() => router.back()} />}
      >
        <EmptyState icon="calendar" message="Term Not Found" subtitle="The requested term could not be found." />
        <Button label="Back" onPress={() => router.back()} variant="secondary" style={{ marginTop: 16 }} />
      </ScreenTemplate>
    );
  }

  const statusText = termIsActive ? t('terms.active') : t('terms.inactive');
  const statusColor = termIsActive ? '#166534' : '#6b7280';

  return (
    <ScreenTemplate
      scrollable={true}
      header={
        <PageHeader
          title={term.term_name}
          onBack={() => router.back()}
          rightElement={
            canManage ? (
              <Button label={t('common.edit')} variant="ghost" onPress={() => router.push(`/manage/terms?edit=${termId}`)} />
            ) : null
          }
        />
      }
    >
      {/* Error Banner */}
      {error && (
        <AlertBanner type="error" message={error} onDismiss={() => setError(null)} />
      )}

      {/* Term Info Card */}
      <View style={[styles.termInfo, { backgroundColor: theme.backgroundElement }]}>
        <View style={styles.termIcon}>
          <Icon name="calendar" size={28} color="#fff" />
        </View>
        <View style={styles.termDetails}>
          <AppText variant="heading" style={styles.termName}>
            {term.term_name}
          </AppText>
          <View style={styles.dateRange}>
            <Icon name="time" size={14} color={theme.textSecondary} />
            <AppText variant="body" color={theme.textSecondary}>
              {formatDate(term.start_date)} - {formatDate(term.end_date)}
            </AppText>
          </View>
          <View style={[styles.statusBadge, termIsActive ? styles.statusActive : styles.statusInactive]}>
            <AppText variant="caption" color={statusColor}>
              {statusText}
            </AppText>
          </View>
        </View>
      </View>

      {/* Stats */}
      <View style={styles.statsGrid}>
        <View style={[styles.statCard, { backgroundColor: '#fef2f2' }]}>
          <Icon name="school" size={24} color={BrandColors.coral} />
          <AppText variant="display" color={BrandColors.coral}>
            {termClasses?.length || 0}
          </AppText>
          <AppText variant="caption" color={theme.textSecondary}>
            Classes
          </AppText>
        </View>
        <View style={[styles.statCard, { backgroundColor: '#f0fdf4' }]}>
          <Icon name="people" size={24} color={BrandColors.teal} />
          <AppText variant="display" color={BrandColors.teal}>
            {termClasses?.reduce((sum, c) => sum + (c.capacity || 0), 0) || 0}
          </AppText>
          <AppText variant="caption" color={theme.textSecondary}>
            Total Capacity
          </AppText>
        </View>
      </View>

      {/* Info Banner */}
      {canManage && !termIsActive && (
        <View style={[styles.infoBanner, { backgroundColor: '#fef3c7' }]}>
          <Icon name="information-circle" size={20} color={BrandColors.coral} />
          <AppText variant="body" style={{ flex: 1 }}>
            This term is not active. Class assignments are read-only.
          </AppText>
        </View>
      )}

      {/* Assigned Classes */}
      <InfoCard
        title={t('terms.assignedClasses')}
        rightElement={
          canManage && termIsActive ? (
            <Button label="Manage" variant="ghost" onPress={() => setShowAddModal(true)} />
          ) : null
        }
      >
        {termClasses && termClasses.length > 0 ? (
          <ScrollView style={styles.classList} showsVerticalScrollIndicator={false}>
            {termClasses.map((cls) => (
              <View key={cls.class_id} style={[styles.classCard, { backgroundColor: theme.backgroundElement }]}>
                <View style={styles.classIcon}>
                  <Icon name="library" size={20} color={BrandColors.coral} />
                </View>
                <View style={styles.classInfo}>
                  <AppText variant="body" style={styles.className}>
                    {cls.class_name}
                  </AppText>
                  <View style={styles.classMeta}>
                    <View style={styles.classMetaItem}>
                      <Icon name="people" size={14} color={theme.textSecondary} />
                      <AppText variant="caption" color={theme.textSecondary}>
                        Cap: {cls.capacity || 'Unlimited'}
                      </AppText>
                    </View>
                  </View>
                </View>
                {canManage && termIsActive && (
                  <Pressable
                    onPress={() => handleUnassignClass(cls.class_id)}
                    disabled={isMutating}
                    style={styles.removeButton}
                  >
                    {isUnassigning ? (
                      <ActivityIndicator size="small" color="#dc2626" />
                    ) : (
                      <Icon name="close-circle" size={20} color="#dc2626" />
                    )}
                  </Pressable>
                )}
              </View>
            ))}
          </ScrollView>
        ) : (
          <View style={styles.emptyState}>
            <AppText style={styles.emptyStateIcon}>📚</AppText>
            <AppText variant="body" color={theme.textSecondary}>
              {t('terms.noAssignedClasses')}
            </AppText>
          </View>
        )}
      </InfoCard>

      {/* Add Class Modal */}
      <Modal
        visible={showAddModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: theme.background }]}>
            <View style={styles.modalHeader}>
              <AppText variant="subheading">Manage Classes</AppText>
              <Pressable onPress={() => setShowAddModal(false)} style={styles.closeButton}>
                <Icon name="close" size={24} color={theme.text} />
              </Pressable>
            </View>

            {/* Search */}
            <View style={[styles.searchContainer, { backgroundColor: theme.backgroundElement }]}>
              <Icon name="search" size={16} color={theme.textSecondary} />
              <TextInput
                style={[styles.searchInput, { color: theme.text }]}
                placeholder="Search classes..."
                placeholderTextColor={theme.textSecondary}
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
            </View>

            {/* Classes List */}
            <ScrollView showsVerticalScrollIndicator={false}>
              <View style={styles.availableGrid}>
                {isLoadingAllClasses ? (
                  <ActivityIndicator size="large" color={BrandColors.coral} />
                ) : (
                  filteredClasses.map((cls) => {
                    const isAssigned = assignedClassIds.has(cls.class_id);
                    return (
                      <Pressable
                        key={cls.class_id}
                        onPress={() =>
                          isAssigned
                            ? handleUnassignClass(cls.class_id)
                            : handleAssignClass(cls.class_id)
                        }
                        disabled={isMutating}
                        style={[
                          styles.availableChip,
                          isAssigned && styles.availableChipAssigned,
                        ]}
                      >
                        {isMutating ? (
                          <ActivityIndicator size="small" color={isAssigned ? '#fff' : theme.text} />
                        ) : (
                          <>
                            <Icon
                              name={isAssigned ? 'checkmark-circle' : 'add-circle'}
                              size={16}
                              color={isAssigned ? '#fff' : theme.textSecondary}
                            />
                            <AppText variant="caption" color={isAssigned ? '#fff' : theme.text}>
                              {cls.class_name}
                            </AppText>
                          </>
                        )}
                      </Pressable>
                    );
                  })
                )}
              </View>
            </ScrollView>

            <Button label={t('common.close')} onPress={() => setShowAddModal(false)} style={{ marginTop: 16 }} />
          </View>
        </View>
      </Modal>
    </ScreenTemplate>
  );
}

const styles = StyleSheet.create({
  termInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    borderRadius: 12,
  },
  termIcon: {
    width: 56,
    height: 56,
    borderRadius: 14,
    backgroundColor: BrandColors.teal,
    justifyContent: 'center',
    alignItems: 'center',
  },
  termDetails: {
    flex: 1,
  },
  termName: {
    fontWeight: '700',
  },
  dateRange: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 4,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginTop: 8,
  },
  statusActive: {
    backgroundColor: '#dcfce7',
  },
  statusInactive: {
    backgroundColor: '#f3f4f6',
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
  },
  infoBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 14,
    borderRadius: 10,
  },
  classList: {
    gap: 8,
  },
  classCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e8e8e8',
    marginBottom: 8,
  },
  classIcon: {
    width: 44,
    height: 44,
    borderRadius: 10,
    backgroundColor: '#FFF7ED',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  classInfo: {
    flex: 1,
  },
  className: {
    fontWeight: '600',
  },
  classMeta: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 4,
  },
  classMetaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  removeButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#fee2e2',
  },
  emptyState: {
    alignItems: 'center',
    padding: 24,
  },
  emptyStateIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  closeButton: {
    padding: 8,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
  },
  availableGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  availableChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#fff',
    gap: 6,
  },
  availableChipAssigned: {
    backgroundColor: BrandColors.teal,
    borderColor: BrandColors.teal,
  },
});
