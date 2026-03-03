/**
 * Organism — ClassAssignments
 *
 * Comprehensive assignment management component for classes.
 * Supports role-based views (Admin/Director/Teacher/Parent).
 *
 * Features:
 * - Tab-based navigation between Students and Teachers
 * - Visual capacity indicator
 * - Assignment cards with avatars
 * - Bulk assignment capabilities
 * - Search/filter functionality
 * - Empty states
 */
import React, { useState, useMemo, useCallback } from 'react';
import {
  View,
  Pressable,
  TextInput,
  Modal,
  ScrollView,
  ActivityIndicator,
} from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { Icon } from '@/components/atoms/icon';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import {
  useGetClassAssignmentsQuery,
  useAssignStudentToClassMutation,
  useUnassignStudentFromClassMutation,
  useAssignTeacherToClassMutation,
  useUnassignTeacherFromClassMutation,
} from '@/store/api/classApi';
import { useListStudentsQuery } from '@/store/api/studentApi';
import { useListTeachersQuery } from '@/store/api/teacherApi';
import { BrandColors } from '@/constants/theme';

import { styles } from './ClassAssignments.styles';
import type {
  ClassAssignmentsProps,
  CapacityIndicatorProps,
} from './ClassAssignments.types';

type TabType = 'students' | 'teachers';

/**
 * Capacity Indicator Component
 */
function CapacityIndicator({ current, capacity, size = 'medium' }: CapacityIndicatorProps) {
  const theme = useTheme();
  
  const percentage = capacity && capacity > 0 ? (current / capacity) * 100 : 0;
  const isFull = capacity !== null && capacity !== undefined && current >= capacity;
  const isNearFull = percentage >= 80 && !isFull;
  
  const fillColor = isFull ? '#dc2626' : isNearFull ? '#f59e0b' : '#22c55e';
  
  const height = size === 'small' ? 6 : size === 'large' ? 12 : 8;
  
  return (
    <View style={styles.capacitySection}>
      <View style={[styles.capacityBar, { height }]}>
        <View
          style={[
            styles.capacityFill,
            { width: `${Math.min(percentage, 100)}%`, backgroundColor: fillColor },
          ]}
        />
      </View>
      <AppText variant="caption" style={styles.capacityText}>
        {capacity !== null && capacity !== undefined
          ? `${current}/${capacity}`
          : `${current} students`}
      </AppText>
    </View>
  );
}

/**
 * Assignment Card Component
 */
interface AssignmentCardProps {
  id: number;
  name: string;
  subtitle?: string;
  type: 'student' | 'teacher';
  canRemove: boolean;
  onRemove: () => void;
  isRemoving: boolean;
}

function AssignmentCard({
  id,
  name,
  subtitle,
  type,
  canRemove,
  onRemove,
  isRemoving,
}: AssignmentCardProps) {
  const theme = useTheme();
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  
  return (
    <View style={styles.assignmentCard}>
      <View
        style={[
          styles.assignmentAvatar,
          type === 'teacher' && styles.assignmentAvatarTeacher,
        ]}
      >
        <AppText variant="label" color="#fff">
          {initials}
        </AppText>
      </View>
      <View style={styles.assignmentInfo}>
        <AppText variant="body" style={styles.assignmentName}>
          {name}
        </AppText>
        {subtitle && (
          <AppText variant="caption" color={theme.textSecondary} style={styles.assignmentMeta}>
            {subtitle}
          </AppText>
        )}
      </View>
      {canRemove && (
        <Pressable
          onPress={onRemove}
          disabled={isRemoving}
          style={[styles.removeButton, isRemoving && styles.removeButtonDisabled]}
        >
          {isRemoving ? (
            <ActivityIndicator size="small" color="#dc2626" />
          ) : (
            <Icon name="close-circle" size={20} color="#dc2626" />
          )}
        </Pressable>
      )}
    </View>
  );
}

/**
 * Available Chip Component
 */
interface AvailableChipProps {
  name: string;
  isAssigned: boolean;
  type: 'student' | 'teacher';
  disabled?: boolean;
  onPress: () => void;
  isLoading: boolean;
}

function AvailableChip({
  name,
  isAssigned,
  type,
  disabled,
  onPress,
  isLoading,
}: AvailableChipProps) {
  const theme = useTheme();
  
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || isLoading}
      style={[
        styles.availableChip,
        isAssigned && styles.availableChipAssigned,
        isAssigned && type === 'teacher' && styles.availableChipTeacher,
        disabled && styles.availableChipDisabled,
      ]}
    >
      {isLoading ? (
        <ActivityIndicator size="small" color={isAssigned ? '#fff' : theme.text} />
      ) : (
        <>
          <Icon
            name={isAssigned ? 'checkmark-circle' : 'add-circle'}
            size={16}
            color={isAssigned ? '#fff' : theme.textSecondary}
          />
          <AppText
            variant="caption"
            color={isAssigned ? '#fff' : theme.text}
            style={styles.availableChipText}
          >
            {name}
          </AppText>
        </>
      )}
    </Pressable>
  );
}

/**
 * Main ClassAssignments Component
 */
export function ClassAssignments({
  classId,
  className,
  termId,
  onAssignmentsChange,
}: ClassAssignmentsProps) {
  const theme = useTheme();
  const { t } = useLocalization();
  const user = useAppSelector(selectCurrentUser);
  
  const [activeTab, setActiveTab] = useState<TabType>('students');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Fetch data
  const { data: assignments, isLoading: isLoadingAssignments } = useGetClassAssignmentsQuery(
    { classId, termId },
    { skip: !classId }
  );
  const { data: studentsData, isLoading: isLoadingStudents } = useListStudentsQuery(
    { pageSize: 500 },
    { skip: !showAddModal || activeTab !== 'students' }
  );
  const { data: teachersData, isLoading: isLoadingTeachers } = useListTeachersQuery(
    { pageSize: 500 },
    { skip: !showAddModal || activeTab !== 'teachers' }
  );
  
  // Mutations
  const [assignStudent, { isLoading: isAssigningStudent }] = useAssignStudentToClassMutation();
  const [unassignStudent, { isLoading: isUnassigningStudent }] = useUnassignStudentFromClassMutation();
  const [assignTeacher, { isLoading: isAssigningTeacher }] = useAssignTeacherToClassMutation();
  const [unassignTeacher, { isLoading: isUnassigningTeacher }] = useUnassignTeacherFromClassMutation();
  
  // Permissions
  const userRole = user?.role;
  const canManageStudents = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  const canManageTeachers = userRole === 'ADMIN' || userRole === 'DIRECTOR';
  const canViewAssignments = true; // All roles can view
  
  // Derived data
  const assignedStudentIds = useMemo(
    () => new Set(assignments?.students.map((s) => s.student_id) || []),
    [assignments]
  );
  const assignedTeacherIds = useMemo(
    () => new Set(assignments?.teachers.map((t) => t.teacher_id) || []),
    [assignments]
  );
  
  const availableStudents = useMemo(() => {
    if (!studentsData?.data) return [];
    return studentsData.data.filter((s) =>
      s.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.last_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [studentsData, searchQuery]);
  
  const availableTeachers = useMemo(() => {
    if (!teachersData?.data) return [];
    return teachersData.data.filter((t) =>
      t.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.last_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [teachersData, searchQuery]);
  
  const atCapacity = useMemo(() => {
    if (!assignments?.capacity) return false;
    return (assignments.current_student_count || 0) >= assignments.capacity;
  }, [assignments]);
  
  // Handlers
  const handleAssignStudent = useCallback(
    async (studentId: number) => {
      try {
        await assignStudent({ classId, data: { student_id: studentId, term_id: termId } }).unwrap();
        onAssignmentsChange?.();
      } catch (error) {
        console.error('Failed to assign student:', error);
      }
    },
    [assignStudent, classId, termId, onAssignmentsChange]
  );
  
  const handleUnassignStudent = useCallback(
    async (studentId: number) => {
      try {
        await unassignStudent({ classId, studentId, termId }).unwrap();
        onAssignmentsChange?.();
      } catch (error) {
        console.error('Failed to unassign student:', error);
      }
    },
    [unassignStudent, classId, termId, onAssignmentsChange]
  );
  
  const handleAssignTeacher = useCallback(
    async (teacherId: number) => {
      try {
        await assignTeacher({ classId, data: { teacher_id: teacherId, term_id: termId } }).unwrap();
        onAssignmentsChange?.();
      } catch (error) {
        console.error('Failed to assign teacher:', error);
      }
    },
    [assignTeacher, classId, termId, onAssignmentsChange]
  );
  
  const handleUnassignTeacher = useCallback(
    async (teacherId: number) => {
      try {
        await unassignTeacher({ classId, teacherId, termId }).unwrap();
        onAssignmentsChange?.();
      } catch (error) {
        console.error('Failed to unassign teacher:', error);
      }
    },
    [unassignTeacher, classId, termId, onAssignmentsChange]
  );
  
  const isLoading = isLoadingAssignments;
  const isMutating =
    isAssigningStudent || isUnassigningStudent || isAssigningTeacher || isUnassigningTeacher;
  
  // Render loading state
  if (isLoading) {
    return (
      <View style={styles.container}>
        <View style={styles.skeletonCard}>
          <View style={styles.skeletonAvatar} />
          <View style={styles.skeletonText} />
        </View>
        <View style={styles.skeletonCard}>
          <View style={styles.skeletonAvatar} />
          <View style={styles.skeletonText} />
        </View>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      {/* Header with Capacity */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <AppText variant="subheading">{className}</AppText>
          {assignments?.term_name && (
            <AppText variant="caption" color={theme.textSecondary}>
              {assignments.term_name}
            </AppText>
          )}
        </View>
        <View style={styles.headerRight}>
          <CapacityIndicator
            current={assignments?.current_student_count || 0}
            capacity={assignments?.capacity}
            size="small"
          />
        </View>
      </View>
      
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <Pressable
          onPress={() => setActiveTab('students')}
          style={[styles.tab, activeTab === 'students' && styles.activeTab]}
        >
          <View style={styles.tabContent}>
            <Icon name="people" size={16} color={activeTab === 'students' ? BrandColors.coral : theme.textSecondary} />
            <AppText
              variant="label"
              color={activeTab === 'students' ? BrandColors.coral : theme.textSecondary}
            >
              Students
            </AppText>
            <View style={[styles.tabBadge, activeTab === 'students' && styles.activeTabBadge]}>
              <AppText variant="caption" color={activeTab === 'students' ? '#fff' : theme.text}>
                {assignments?.students.length || 0}
              </AppText>
            </View>
          </View>
        </Pressable>
        
        <Pressable
          onPress={() => setActiveTab('teachers')}
          style={[styles.tab, activeTab === 'teachers' && styles.activeTab]}
        >
          <View style={styles.tabContent}>
            <Icon name="school" size={16} color={activeTab === 'teachers' ? BrandColors.teal : theme.textSecondary} />
            <AppText
              variant="label"
              color={activeTab === 'teachers' ? BrandColors.teal : theme.textSecondary}
            >
              Teachers
            </AppText>
            <View style={[styles.tabBadge, activeTab === 'teachers' && styles.activeTabBadge]}>
              <AppText variant="caption" color={activeTab === 'teachers' ? '#fff' : theme.text}>
                {assignments?.teachers.length || 0}
              </AppText>
            </View>
          </View>
        </Pressable>
      </View>
      
      {/* Students Tab */}
      {activeTab === 'students' && (
        <>
          {/* Section Header */}
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitle}>
              <AppText variant="label" color={theme.textSecondary}>
                🎓 Assigned Students
              </AppText>
            </View>
            {canManageStudents && (
              <Button
                label="Add"
                variant="ghost"
                onPress={() => setShowAddModal(true)}
                disabled={atCapacity}
              />
            )}
          </View>
          
          {/* Students List */}
          <ScrollView style={styles.assignmentsList} showsVerticalScrollIndicator={false}>
            {assignments?.students && assignments.students.length > 0 ? (
              assignments.students.map((student) => (
                <AssignmentCard
                  key={student.student_id}
                  id={student.student_id}
                  name={student.student_name || `Student #${student.student_id}`}
                  type="student"
                  canRemove={canManageStudents}
                  onRemove={() => handleUnassignStudent(student.student_id)}
                  isRemoving={isUnassigningStudent}
                />
              ))
            ) : (
              <View style={styles.emptyState}>
                <AppText style={styles.emptyStateIcon}>👥</AppText>
                <AppText variant="body" color={theme.textSecondary}>
                  No students assigned yet
                </AppText>
              </View>
            )}
          </ScrollView>
          
          {/* Capacity Warning */}
          {atCapacity && canManageStudents && (
            <View style={{ marginTop: 12, padding: 12, backgroundColor: '#fef3c7', borderRadius: 8 }}>
              <AppText variant="caption" color="#92400e">
                ⚠️ Class is at capacity. Remove a student to add new ones.
              </AppText>
            </View>
          )}
        </>
      )}
      
      {/* Teachers Tab */}
      {activeTab === 'teachers' && (
        <>
          {/* Section Header */}
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitle}>
              <AppText variant="label" color={theme.textSecondary}>
                👨‍🏫 Assigned Teachers
              </AppText>
            </View>
            {canManageTeachers && (
              <Button
                label="Add"
                variant="ghost"
                onPress={() => setShowAddModal(true)}
              />
            )}
          </View>
          
          {/* Teachers List */}
          <ScrollView style={styles.assignmentsList} showsVerticalScrollIndicator={false}>
            {assignments?.teachers && assignments.teachers.length > 0 ? (
              assignments.teachers.map((teacher) => (
                <AssignmentCard
                  key={teacher.teacher_id}
                  id={teacher.teacher_id}
                  name={teacher.teacher_name || `Teacher #${teacher.teacher_id}`}
                  type="teacher"
                  canRemove={canManageTeachers}
                  onRemove={() => handleUnassignTeacher(teacher.teacher_id)}
                  isRemoving={isUnassigningTeacher}
                />
              ))
            ) : (
              <View style={styles.emptyState}>
                <AppText style={styles.emptyStateIcon}>👨‍🏫</AppText>
                <AppText variant="body" color={theme.textSecondary}>
                  No teachers assigned yet
                </AppText>
              </View>
            )}
          </ScrollView>
        </>
      )}
      
      {/* Add Modal */}
      <Modal
        visible={showAddModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <AppText variant="subheading" style={styles.modalTitle}>
                Add {activeTab === 'students' ? 'Students' : 'Teachers'}
              </AppText>
              <Pressable onPress={() => setShowAddModal(false)} style={styles.closeButton}>
                <Icon name="close" size={24} color={theme.text} />
              </Pressable>
            </View>
            
            {/* Search */}
            <View style={styles.searchContainer}>
              <Icon name="search" size={16} color={theme.textSecondary} />
              <TextInput
                style={[styles.searchInput, { color: theme.text }]}
                placeholder={`Search ${activeTab}...`}
                placeholderTextColor={theme.textSecondary}
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
            </View>
            
            {/* Available Items */}
            <ScrollView showsVerticalScrollIndicator={false}>
              <View style={styles.availableGrid}>
                {activeTab === 'students'
                  ? availableStudents.map((student) => (
                      <AvailableChip
                        key={student.student_id}
                        name={`${student.first_name} ${student.last_name}`}
                        isAssigned={assignedStudentIds.has(student.student_id)}
                        type="student"
                        disabled={atCapacity && !assignedStudentIds.has(student.student_id)}
                        onPress={() =>
                          assignedStudentIds.has(student.student_id)
                            ? handleUnassignStudent(student.student_id)
                            : handleAssignStudent(student.student_id)
                        }
                        isLoading={isMutating}
                      />
                    ))
                  : availableTeachers.map((teacher) => (
                      <AvailableChip
                        key={teacher.user_id}
                        name={`${teacher.first_name} ${teacher.last_name}`}
                        isAssigned={assignedTeacherIds.has(teacher.user_id)}
                        type="teacher"
                        onPress={() =>
                          assignedTeacherIds.has(teacher.user_id)
                            ? handleUnassignTeacher(teacher.user_id)
                            : handleAssignTeacher(teacher.user_id)
                        }
                        isLoading={isMutating}
                      />
                    ))}
              </View>
            </ScrollView>
            
            <Button
              label="Done"
              onPress={() => setShowAddModal(false)}
              style={{ marginTop: 16 }}
            />
          </View>
        </View>
      </Modal>
    </View>
  );
}
