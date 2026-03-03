/**
 * Term Management Screen
 *
 * Role-based functionality:
 * - ADMIN/DIRECTOR: can create, edit, delete terms, and assign classes
 * - All users: can view terms and term details
 */
import { useRouter } from 'expo-router';
import React, { useEffect, useMemo, useState } from 'react';
import { Platform, Pressable, StyleSheet, View } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { AppTextInput } from '@/components/atoms/text-input';
import { AlertBanner } from '@/components/molecules/alert-banner';
import { EmptyState } from '@/components/molecules/empty-state';
import { InfoCard } from '@/components/molecules/info-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { PageHeader } from '@/components/molecules/page-header';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useLocalization } from '@/hooks/use-localization';
import { useTheme } from '@/hooks/use-theme';
import { BrandColors } from '@/constants/theme';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { useListClassesQuery, type ClassResponse } from '@/store/api/classApi';
import {
  useListTermsQuery,
  useGetActiveTermBySchoolQuery,
  useGetTermsBySchoolQuery,
  useGetClassesByTermQuery,
  useCreateTermMutation,
  useUpdateTermMutation,
  useDeleteTermMutation,
  useAssignClassToTermMutation,
  useUnassignClassFromTermMutation,
  type TermResponse,
} from '@/store/api/termApi';

const CLASS_PAGE_SIZE = 200;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!error || typeof error !== 'object') return fallback;
  const err = error as { status?: number; data?: { detail?: string } };
  if (typeof err.data?.detail === 'string') return err.data.detail;
  if (err.status === 404) return 'Not found.';
  if (err.status === 409) return 'Conflict: unable to complete request.';
  if (err.status === 400) return 'Bad request. Please check the input values.';
  return fallback;
};

const formatDate = (value: string | null) => {
  if (!value) return '—';
  return value.split('T')[0];
};

export default function TermsManagementScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;
  const canManage = userRole === 'ADMIN' || userRole === 'DIRECTOR';

  const [selectedSchoolId, setSelectedSchoolId] = useState<number | undefined>(user?.school_id || undefined);
  const [showForm, setShowForm] = useState(false);
  const [editingTermId, setEditingTermId] = useState<number | null>(null);
  const [selectedTermId, setSelectedTermId] = useState<number | null>(null);
  const [termName, setTermName] = useState('');
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [showStartPicker, setShowStartPicker] = useState(false);
  const [showEndPicker, setShowEndPicker] = useState(false);
  const [termImageUrl, setTermImageUrl] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const [assignmentError, setAssignmentError] = useState<string | null>(null);
  const [listError, setListError] = useState<string | null>(null);

  const { data: schools } = useListSchoolsQuery(undefined, { skip: userRole !== 'ADMIN' });

  const { data: terms, isLoading: isTermsLoading, error: termsError } = useListTermsQuery();
  const { data: schoolTerms, isLoading: isSchoolTermsLoading } = useGetTermsBySchoolQuery(selectedSchoolId || 0, {
    skip: !selectedSchoolId,
  });
  const { data: activeTerm, error: activeTermError } = useGetActiveTermBySchoolQuery(selectedSchoolId || 0, {
    skip: !selectedSchoolId,
  });
  const { data: classesData } = useListClassesQuery({ page: 1, pageSize: CLASS_PAGE_SIZE }, { skip: !canManage });

  const [createTerm, { isLoading: isCreating }] = useCreateTermMutation();
  const [updateTerm, { isLoading: isUpdating }] = useUpdateTermMutation();
  const [deleteTerm, { isLoading: isDeleting }] = useDeleteTermMutation();
  const [assignClass, { isLoading: isAssigning }] = useAssignClassToTermMutation();
  const [unassignClass, { isLoading: isUnassigning }] = useUnassignClassFromTermMutation();

  useEffect(() => {
    if (userRole === 'ADMIN' && schools && schools.length > 0 && !selectedSchoolId) {
      setSelectedSchoolId(schools[0].school_id);
    }
  }, [schools, userRole, selectedSchoolId]);

  useEffect(() => {
    if (!termsError) {
      setListError(null);
    } else {
      setListError(getErrorMessage(termsError, t('common.error')));
    }
  }, [termsError, t]);

  const termsForSchool = useMemo(() => {
    if (selectedSchoolId) {
      return schoolTerms || [];
    }
    if (userRole === 'DIRECTOR' && user?.school_id) {
      return terms?.filter((term) => term.school_id === user.school_id) || [];
    }
    return terms || [];
  }, [terms, schoolTerms, userRole, user?.school_id, selectedSchoolId]);

  const activeTermLabel = useMemo(() => {
    if (!activeTerm) return t('terms.noActiveTerm');
    return `${activeTerm.term_name} (${formatDate(activeTerm.start_date)} - ${formatDate(activeTerm.end_date)})`;
  }, [activeTerm, t]);

  const { data: assignedClasses } = useGetClassesByTermQuery(selectedTermId || 0, {
    skip: !selectedTermId,
  });

  const selectedTerm = useMemo(() => {
    if (!selectedTermId) return null;
    return termsForSchool.find((term) => term.term_id === selectedTermId) || null;
  }, [termsForSchool, selectedTermId]);

  const availableClasses = useMemo(() => {
    const classes = classesData?.data || [];
    if (userRole === 'ADMIN') {
      if (!selectedSchoolId) return [];
      return classes.filter((cls) => cls.school_id === selectedSchoolId);
    }
    if (userRole === 'DIRECTOR' && user?.school_id) {
      return classes.filter((cls) => cls.school_id === user.school_id);
    }
    return classes;
  }, [classesData, selectedSchoolId, userRole, user?.school_id]);

  const assignedClassIds = new Set((assignedClasses || []).map((cls) => cls.class_id));
  const assignedClassCount = selectedTermId ? assignedClasses?.length || 0 : 0;

  const handleStartChange = (_event: unknown, date?: Date) => {
    setShowStartPicker(false);
    if (date) setStartDate(date);
  };

  const handleEndChange = (_event: unknown, date?: Date) => {
    setShowEndPicker(false);
    if (date) setEndDate(date);
  };

  const resetForm = () => {
    setEditingTermId(null);
    setTermName('');
    setStartDate(new Date());
    setEndDate(null);
    setTermImageUrl('');
    setIsActive(true);
    setFormError(null);
  };

  const handleEdit = (term: TermResponse) => {
    setEditingTermId(term.term_id);
    setTermName(term.term_name);
    setStartDate(new Date(term.start_date));
    setEndDate(term.end_date ? new Date(term.end_date) : null);
    setTermImageUrl(term.term_img_url || '');
    setIsActive(term.activity_status);
    setFormError(null);
    setShowForm(true);
  };

  const handleSubmit = async () => {
    if (!termName.trim()) {
      setFormError(t('terms.nameRequired'));
      return;
    }

    const targetSchoolId = selectedSchoolId || user?.school_id;
    if (!targetSchoolId) {
      setFormError(t('terms.schoolRequired'));
      return;
    }

    if (endDate && startDate > endDate) {
      setFormError(t('terms.invalidDateRange'));
      return;
    }

    const trimmedImageUrl = termImageUrl.trim();
    if (trimmedImageUrl && !trimmedImageUrl.startsWith('http')) {
      setFormError(t('terms.invalidImageUrl'));
      return;
    }

    const payload = {
      term_name: termName.trim(),
      school_id: targetSchoolId,
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate ? endDate.toISOString().split('T')[0] : null,
      activity_status: isActive,
      term_img_url: trimmedImageUrl || null,
    };

    try {
      if (editingTermId) {
        await updateTerm({ termId: editingTermId, data: payload }).unwrap();
      } else {
        await createTerm(payload).unwrap();
      }
      setShowForm(false);
      resetForm();
    } catch (error) {
      setFormError(getErrorMessage(error, t('terms.saveFailed')));
    }
  };

  const handleDelete = async (termId: number) => {
    try {
      await deleteTerm(termId).unwrap();
    } catch (error) {
      setListError(getErrorMessage(error, t('terms.deleteFailed')));
    }
  };

  const toggleAssignment = async (cls: ClassResponse) => {
    if (!selectedTermId) return;
    setAssignmentError(null);
    try {
      if (assignedClassIds.has(cls.class_id)) {
        await unassignClass({ termId: selectedTermId, classId: cls.class_id }).unwrap();
      } else {
        await assignClass({ termId: selectedTermId, classId: cls.class_id }).unwrap();
      }
    } catch (error) {
      setAssignmentError(getErrorMessage(error, t('terms.assignFailed')));
    }
  };

  const isLoading = isTermsLoading || isSchoolTermsLoading;

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('terms.title')}
          onBack={() => router.back()}
        />
      }
    >
      {userRole === 'ADMIN' && schools && schools.length > 0 ? (
        <View style={styles.section}>
          <AppText variant="label" color={theme.textSecondary}>
            {t('terms.selectSchool')}
          </AppText>
          <View style={styles.selectorRow}>
            {schools.map((school) => (
              <Pressable
                key={school.school_id}
                onPress={() => setSelectedSchoolId(school.school_id)}
                style={[
                  styles.selectorButton,
                  selectedSchoolId === school.school_id && { backgroundColor: BrandColors.coral },
                ]}
              >
                <AppText
                  variant="caption"
                  color={selectedSchoolId === school.school_id ? '#fff' : theme.text}
                >
                  {school.school_name}
                </AppText>
              </Pressable>
            ))}
          </View>
        </View>
      ) : null}

      {selectedSchoolId ? (
        <View style={[styles.activeCard, { backgroundColor: theme.backgroundElement }]}
        >
          <AppText variant="label" color={theme.textSecondary}>
            {t('terms.activeTerm')}
          </AppText>
          <AppText variant="body" style={styles.activeText}>
            {activeTermError ? t('terms.noActiveTerm') : activeTermLabel}
          </AppText>
        </View>
      ) : null}
      {!selectedSchoolId ? (
        <AlertBanner type="info" message={t('terms.selectSchoolHint')} />
      ) : null}

      {canManage ? (
        <Button
          label={showForm ? t('common.cancel') : t('terms.create')}
          onPress={() => {
            if (showForm) {
              setShowForm(false);
              resetForm();
            } else {
              setShowForm(true);
            }
          }}
          variant={showForm ? 'secondary' : 'primary'}
          style={styles.createButton}
        />
      ) : null}

      {showForm && canManage ? (
        <View style={[styles.formCard, { backgroundColor: theme.backgroundElement }]}
        >
          <AppText variant="subheading" style={styles.formTitle}>
            {editingTermId ? t('terms.edit') : t('terms.create')}
          </AppText>
          {formError ? <AlertBanner type="error" message={formError} /> : null}
          <AppTextInput
            label={t('terms.name')}
            value={termName}
            onChangeText={setTermName}
            placeholder={t('terms.name')}
          />
          <AppTextInput
            label={t('terms.imageUrl')}
            value={termImageUrl}
            onChangeText={setTermImageUrl}
            placeholder={t('terms.imageUrlPlaceholder')}
          />
          <View style={styles.inputGroup}>
            <AppText variant="caption" color={theme.textSecondary}>
              {t('terms.startDate')}
            </AppText>
            {Platform.OS === 'web' ? (
              <input
                type="date"
                value={startDate.toISOString().split('T')[0]}
                onChange={(event) => setStartDate(new Date(event.target.value))}
                style={styles.dateInput as any}
              />
            ) : (
              <Pressable
                onPress={() => setShowStartPicker(true)}
                style={[styles.dateButton, { backgroundColor: theme.backgroundElement }]}
              >
                <AppText variant="body">{startDate.toISOString().split('T')[0]}</AppText>
              </Pressable>
            )}
            {showStartPicker && (
              <DateTimePicker
                value={startDate}
                mode="date"
                display="default"
                onChange={handleStartChange}
              />
            )}
          </View>
          <View style={styles.inputGroup}>
            <AppText variant="caption" color={theme.textSecondary}>
              {t('terms.endDate')}
            </AppText>
            {Platform.OS === 'web' ? (
              <input
                type="date"
                value={endDate ? endDate.toISOString().split('T')[0] : ''}
                onChange={(event) => setEndDate(event.target.value ? new Date(event.target.value) : null)}
                style={styles.dateInput as any}
              />
            ) : (
              <Pressable
                onPress={() => setShowEndPicker(true)}
                style={[styles.dateButton, { backgroundColor: theme.backgroundElement }]}
              >
                <AppText variant="body">{endDate ? endDate.toISOString().split('T')[0] : t('terms.noEndDate')}</AppText>
              </Pressable>
            )}
            {showEndPicker && (
              <DateTimePicker
                value={endDate || new Date()}
                mode="date"
                display="default"
                onChange={handleEndChange}
              />
            )}
          </View>
          <View style={styles.selectorRow}>
            <Pressable
              onPress={() => setIsActive(true)}
              style={[
                styles.selectorButton,
                isActive && { backgroundColor: BrandColors.coral },
              ]}
            >
              <AppText variant="caption" color={isActive ? '#fff' : theme.text}>
                {t('terms.active')}
              </AppText>
            </Pressable>
            <Pressable
              onPress={() => setIsActive(false)}
              style={[
                styles.selectorButton,
                !isActive && { backgroundColor: BrandColors.coral },
              ]}
            >
              <AppText variant="caption" color={!isActive ? '#fff' : theme.text}>
                {t('terms.inactive')}
              </AppText>
            </Pressable>
          </View>
          <Button
            label={editingTermId ? t('common.save') : t('terms.create')}
            onPress={handleSubmit}
            isLoading={isCreating || isUpdating}
            disabled={!termName.trim()}
          />
        </View>
      ) : null}

      {listError ? <AlertBanner type="error" message={listError} /> : null}

      {isLoading ? (
        <LoadingState cardCount={3} />
      ) : termsForSchool.length > 0 ? (
        termsForSchool.map((term) => (
          <InfoCard
            key={term.term_id}
            title={term.term_name}
            subtitle={`${formatDate(term.start_date)} - ${formatDate(term.end_date)}`}
            rightElement={
              canManage ? (
                <View style={styles.cardActions}>
                  <Button
                    label={t('common.edit')}
                    variant="secondary"
                    fullWidth={false}
                    onPress={() => handleEdit(term)}
                    disabled={isDeleting}
                  />
                  <Button
                    label={t('common.delete')}
                    variant="ghost"
                    fullWidth={false}
                    onPress={() => handleDelete(term.term_id)}
                    isLoading={isDeleting}
                    disabled={isDeleting}
                  />
                </View>
              ) : null
            }
            onPress={() => router.push(`/term/${term.term_id}`)}
          >
            <View style={styles.termMeta}>
              <AppText variant="caption" color={theme.textSecondary}>
                {t('terms.status')}: {term.activity_status ? t('terms.active') : t('terms.inactive')}
              </AppText>
              {term.term_img_url ? (
                <AppText variant="caption" color={theme.textSecondary}>
                  {t('terms.imageAttached')}
                </AppText>
              ) : null}
              {selectedTermId === term.term_id ? (
                <AppText variant="caption" color={theme.textSecondary}>
                  {t('terms.classCount', { count: assignedClassCount })}
                </AppText>
              ) : null}
            </View>
            {selectedTermId === term.term_id ? (
              <View style={styles.assignSection}>
                <AppText variant="label" color={theme.textSecondary}>
                  {t('terms.assignedClasses')}
                </AppText>
                {assignmentError ? <AlertBanner type="error" message={assignmentError} /> : null}
                {assignedClasses && assignedClasses.length > 0 ? (
                  <View style={styles.selectorRow}>
                    {assignedClasses.map((cls) => (
                      <View key={cls.class_id} style={styles.assignedChip}>
                        <AppText variant="caption" color={theme.text}>
                          {cls.class_name}
                        </AppText>
                      </View>
                    ))}
                  </View>
                ) : (
                  <AppText variant="caption" color={theme.textSecondary}>
                    {t('terms.noAssignedClasses')}
                  </AppText>
                )}
                {canManage ? (
                  <View style={styles.assignList}>
                    <AppText variant="label" color={theme.textSecondary}>
                      {t('terms.manageClasses')}
                    </AppText>
                    {availableClasses.length > 0 ? (
                      <View style={styles.selectorRow}>
                        {availableClasses.map((cls) => {
                          const assigned = assignedClassIds.has(cls.class_id);
                          return (
                            <Pressable
                              key={cls.class_id}
                              onPress={() => toggleAssignment(cls)}
                              disabled={isAssigning || isUnassigning}
                              style={[
                                styles.selectorButton,
                                assigned && { backgroundColor: BrandColors.coral },
                              ]}
                            >
                              <AppText
                                variant="caption"
                                color={assigned ? '#fff' : theme.text}
                              >
                                {cls.class_name}
                              </AppText>
                            </Pressable>
                          );
                        })}
                      </View>
                    ) : (
                      <AppText variant="caption" color={theme.textSecondary}>
                        {t('terms.noClassesAvailable')}
                      </AppText>
                    )}
                  </View>
                ) : null}
              </View>
            ) : null}
          </InfoCard>
        ))
      ) : (
        <EmptyState
          icon="calendar"
          message={t('terms.noTerms')}
          subtitle={t('terms.noTermsSubtitle')}
        />
      )}
    </ScreenTemplate>
  );
}

const styles = StyleSheet.create({
  section: {
    gap: 8,
  },
  selectorRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  selectorButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  createButton: {
    marginTop: 8,
  },
  formCard: {
    padding: 16,
    borderRadius: 16,
    gap: 12,
  },
  formTitle: {
    marginBottom: 4,
  },
  inputGroup: {
    gap: 8,
  },
  dateButton: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  dateInput: {
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: '#fff',
    fontSize: 16,
  },
  activeCard: {
    padding: 16,
    borderRadius: 16,
    gap: 6,
  },
  activeText: {
    fontWeight: '600',
  },
  cardActions: {
    flexDirection: 'row',
    gap: 8,
  },
  termMeta: {
    marginTop: 8,
    gap: 4,
  },
  assignSection: {
    marginTop: 12,
    gap: 8,
  },
  assignList: {
    marginTop: 12,
    gap: 8,
  },
  assignedChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#eee',
    backgroundColor: '#f8f8f8',
  },
});
