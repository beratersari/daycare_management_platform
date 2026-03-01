/**
 * Classes Management Screen
 *
 * Page (Atomic Design):
 * - Uses ScreenTemplate for consistent layout
 * - Uses PageHeader for navigation
 * - Uses InfoCard molecules for class cards
 * - Uses LoadingState and EmptyState for UX consistency
 */
import { useRouter } from 'expo-router';
import React, { useEffect, useMemo, useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { FormField } from '@/components/molecules/form-field';
import { PageHeader } from '@/components/molecules/page-header';
import { InfoCard } from '@/components/molecules/info-card';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { ScreenTemplate } from '@/components/templates/screen-template';
import { useLocalization } from '@/hooks/use-localization';
import { useTheme } from '@/hooks/use-theme';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import {
  useListClassesQuery,
  useCreateClassMutation,
  useUpdateClassMutation,
  useDeleteClassMutation,
  type ClassResponse,
} from '@/store/api/classApi';
import {
  useListStudentsQuery,
  useEnrollStudentInClassMutation,
  useUnenrollStudentFromClassMutation,
} from '@/store/api/studentApi';
import { useListSchoolsQuery } from '@/store/api/schoolApi';
import { BrandColors } from '@/constants/theme';

export default function ClassesManagementScreen() {
  const router = useRouter();
  const { t } = useLocalization();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  const userRole = user?.role;
  const canManageClasses = userRole === 'ADMIN' || userRole === 'DIRECTOR' || userRole === 'TEACHER';

  const { data: classesData, isLoading } = useListClassesQuery({ pageSize: 100 }, { skip: !canManageClasses });
  const classes = classesData?.data || [];

  const { data: studentsData } = useListStudentsQuery({ pageSize: 200 }, { skip: !canManageClasses });
  const students = studentsData?.data || [];

  const { data: schools } = useListSchoolsQuery(undefined, { skip: userRole !== 'ADMIN' });
  const [createClass, { isLoading: isCreating }] = useCreateClassMutation();
  const [updateClass, { isLoading: isUpdating }] = useUpdateClassMutation();
  const [deleteClass, { isLoading: isDeleting }] = useDeleteClassMutation();
  const [enrollStudent, { isLoading: isEnrolling }] = useEnrollStudentInClassMutation();
  const [unenrollStudent, { isLoading: isUnenrolling }] = useUnenrollStudentFromClassMutation();

  const [selectedSchoolId, setSelectedSchoolId] = useState<number | undefined>(user?.school_id || undefined);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingClassId, setEditingClassId] = useState<number | null>(null);
  const [className, setClassName] = useState('');
  const [capacity, setCapacity] = useState('');

  useEffect(() => {
    if (userRole === 'ADMIN' && schools && schools.length > 0 && !selectedSchoolId) {
      setSelectedSchoolId(schools[0].school_id);
    }
  }, [schools, userRole, selectedSchoolId]);

  const visibleClasses = useMemo(() => {
    if (userRole === 'ADMIN') {
      if (!selectedSchoolId) return [];
      return classes.filter((cls) => cls.school_id === selectedSchoolId);
    }
    if (userRole === 'DIRECTOR' && user?.school_id) {
      return classes.filter((cls) => cls.school_id === user.school_id);
    }
    return classes;
  }, [classes, selectedSchoolId, userRole, user?.school_id]);

  const availableStudents = useMemo(() => {
    if (userRole === 'ADMIN') {
      if (!selectedSchoolId) return [];
      return students.filter((student) => student.school_id === selectedSchoolId);
    }
    if (userRole === 'DIRECTOR' && user?.school_id) {
      return students.filter((student) => student.school_id === user.school_id);
    }
    return students;
  }, [students, selectedSchoolId, userRole, user?.school_id]);

  const handleEditClass = (cls: ClassResponse) => {
    setEditingClassId(cls.class_id);
    setClassName(cls.class_name);
    setCapacity(cls.capacity ? cls.capacity.toString() : '');
    setShowCreateForm(true);
  };

  const handleCancelEdit = () => {
    setEditingClassId(null);
    setClassName('');
    setCapacity('');
    setShowCreateForm(false);
  };

  const handleSaveClass = async () => {
    if (!className.trim()) return;
    const payload = {
      class_name: className.trim(),
      school_id: selectedSchoolId || user?.school_id || 0,
      capacity: capacity ? Number(capacity) : null,
    };

    if (!payload.school_id) return;

    try {
      if (editingClassId) {
        await updateClass({ classId: editingClassId, data: payload }).unwrap();
      } else {
        await createClass(payload).unwrap();
      }
      handleCancelEdit();
    } catch (error) {
      console.error('Failed to save class', error);
    }
  };

  const handleDeleteClass = async (classId: number) => {
    try {
      await deleteClass(classId).unwrap();
    } catch (error) {
      console.error('Failed to delete class', error);
    }
  };

  const toggleEnrollment = async (studentId: number, classId: number, enrolled: boolean) => {
    try {
      if (enrolled) {
        await unenrollStudent({ studentId, classId }).unwrap();
      } else {
        await enrollStudent({ studentId, classId }).unwrap();
      }
    } catch (error) {
      console.error('Failed to update enrollment', error);
    }
  };

  const enrollmentLoading = isEnrolling || isUnenrolling;

  if (!canManageClasses) {
    return (
      <ScreenTemplate
        header={
          <PageHeader
            title={t('dashboard.manageClasses')}
            onBack={() => router.back()}
          />
        }
      >
        <EmptyState
          icon="🔒"
          message={t('class.accessDenied')}
          subtitle={t('class.accessDeniedSubtitle')}
        />
      </ScreenTemplate>
    );
  }

  return (
    <ScreenTemplate
      header={
        <PageHeader
          title={t('dashboard.manageClasses')}
          onBack={() => router.back()}
        />
      }>
      {userRole === 'ADMIN' && schools && schools.length > 0 ? (
        <View style={styles.section}>
          <AppText variant="label" color={theme.textSecondary}>
            {t('events.selectSchool')}
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

      {canManageClasses ? (
        <Button
          label={showCreateForm ? t('common.cancel') : t('class.createClass')}
          onPress={() => (showCreateForm ? handleCancelEdit() : setShowCreateForm(true))}
          variant={showCreateForm ? 'secondary' : 'primary'}
          style={styles.createButton}
        />
      ) : null}

      {showCreateForm ? (
        <View style={[styles.formCard, { backgroundColor: theme.backgroundElement }]}>
          <AppText variant="subheading" style={styles.formTitle}>
            {editingClassId ? t('class.editClass') : t('class.createClass')}
          </AppText>
          <FormField
            label={t('class.name')}
            value={className}
            onChangeText={setClassName}
            placeholder={t('class.name')}
          />
          <FormField
            label={t('class.capacity')}
            value={capacity}
            onChangeText={setCapacity}
            placeholder={t('class.capacity')}
            keyboardType="numeric"
          />
          <Button
            label={editingClassId ? t('common.save') : t('class.createClass')}
            onPress={handleSaveClass}
            isLoading={isCreating || isUpdating}
            disabled={!className.trim()}
          />
        </View>
      ) : null}

      {isLoading ? (
        <LoadingState cardCount={3} />
      ) : visibleClasses.length > 0 ? (
        visibleClasses.map((cls) => (
          <InfoCard
            key={cls.class_id}
            title={cls.class_name}
            subtitle={`${t('class.capacity')}: ${cls.capacity ?? t('class.capacityUnlimited')}`}
            rightElement={
              <View style={styles.cardActions}>
                <Button
                  label={t('common.edit')}
                  variant="secondary"
                  fullWidth={false}
                  onPress={() => handleEditClass(cls)}
                  disabled={isDeleting}
                />
                <Button
                  label={t('common.delete')}
                  variant="ghost"
                  fullWidth={false}
                  onPress={() => handleDeleteClass(cls.class_id)}
                  isLoading={isDeleting}
                  disabled={isDeleting}
                />
              </View>
            }
          >
            <View style={styles.assignedSection}>
              <AppText variant="label" color={theme.textSecondary}>
                {t('class.assignedStudents')}
              </AppText>
              {cls.students.length > 0 ? (
                <View style={styles.selectorRow}>
                  {cls.students.map((student) => (
                    <View key={student.student_id} style={styles.assignedChip}>
                      <AppText variant="caption" color={theme.text}>
                        {student.first_name} {student.last_name}
                      </AppText>
                    </View>
                  ))}
                </View>
              ) : (
                <AppText variant="caption" color={theme.textSecondary}>
                  {t('class.noAssignedStudents')}
                </AppText>
              )}
            </View>
            <View style={styles.enrollmentSection}>
              <AppText variant="label" color={theme.textSecondary}>
                {t('class.enrollStudents')}
              </AppText>
              {availableStudents.length > 0 ? (
                <View style={styles.selectorRow}>
                  {availableStudents.map((student) => {
                    const enrolled = student.class_ids.includes(cls.class_id);
                    return (
                      <Pressable
                        key={student.student_id}
                        onPress={() => toggleEnrollment(student.student_id, cls.class_id, enrolled)}
                        disabled={enrollmentLoading}
                        style={[
                          styles.selectorButton,
                          enrolled && { backgroundColor: BrandColors.coral },
                          enrollmentLoading && styles.selectorButtonDisabled,
                        ]}
                      >
                        <AppText
                          variant="caption"
                          color={enrolled ? '#fff' : theme.text}
                        >
                          {student.first_name} {student.last_name}
                        </AppText>
                      </Pressable>
                    );
                  })}
                </View>
              ) : (
                <AppText variant="caption" color={theme.textSecondary}>
                  {t('class.noStudentsAvailable')}
                </AppText>
              )}
            </View>
          </InfoCard>
        ))
      ) : (
        <EmptyState
          icon="🏫"
          message={t('class.noClasses')}
          subtitle={t('class.noClassesSubtitle')}
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
  selectorButtonDisabled: {
    opacity: 0.6,
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
  cardActions: {
    flexDirection: 'row',
    gap: 8,
  },
  assignedSection: {
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
  enrollmentSection: {
    marginTop: 12,
    gap: 8,
  },
});
