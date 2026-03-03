/**
 * Organism — TermAssignments
 *
 * Comprehensive term-class assignment management component.
 * Allows admins/directors to assign classes to terms.
 */
import React, { useState, useMemo, useCallback } from 'react';
import {
  View,
  ScrollView,
  Pressable,
  Modal,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';

import { AppText } from '@/components/atoms/app-text';
import { Button } from '@/components/atoms/button';
import { Icon } from '@/components/atoms/icon';
import { useTheme } from '@/hooks/use-theme';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import {
  useGetTermsBySchoolQuery,
  useGetClassesByTermQuery,
  useAssignClassToTermMutation,
  useUnassignClassFromTermMutation,
  type TermResponse,
  type TermClassResponse,
} from '@/store/api/termApi';
import { useListClassesQuery, type ClassResponse } from '@/store/api/classApi';
import { BrandColors } from '@/constants/theme';

import { styles } from './TermAssignments.styles';
import type { TermCardProps, ClassCardProps } from './TermAssignments.types';

// Helper to format date
const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return 'Ongoing';
  return dateStr.split('T')[0];
};

// Helper to check if term is active
const isTermActive = (term: TermResponse) => {
  if (!term.activity_status) return false;
  if (term.end_date && new Date(term.end_date) < new Date()) return false;
  return true;
};

/**
 * Term Card Component
 */
function TermCard({
  term,
  classCount,
  isSelected,
  onPress,
}: TermCardProps) {
  const theme = useTheme();
  const isActive = isTermActive(term);
  
  const statusColor = isActive
    ? '#22c55e'
    : term.end_date && new Date(term.end_date) < new Date()
    ? '#6b7280'
    : '#f59e0b';
  
  const statusText = isActive
    ? 'Active'
    : term.end_date && new Date(term.end_date) < new Date()
    ? 'Ended'
    : 'Upcoming';
  
  return (
    <Pressable
      onPress={onPress}
      style={[
        styles.termCard,
        { backgroundColor: theme.backgroundElement },
        isSelected && { borderColor: BrandColors.coral, borderWidth: 2 },
      ]}
    >
      <View style={styles.termHeader}>
        <View style={styles.termInfo}>
          <AppText variant="subheading" style={styles.termName}>
            {term.term_name}
          </AppText>
          <View style={styles.termDates}>
            <Icon name="calendar" size={14} color={theme.textSecondary} />
            <AppText variant="caption" color={theme.textSecondary}>
              {formatDate(term.start_date)} - {formatDate(term.end_date)}
            </AppText>
          </View>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: statusColor + '20' }]}>
          <AppText variant="caption" color={statusColor}>
            {statusText}
          </AppText>
        </View>
      </View>
      
      <View style={styles.termStats}>
        <Icon name="school" size={18} color={BrandColors.teal} />
        <AppText variant="body" style={styles.statValue}>
          {classCount}
        </AppText>
        <AppText variant="caption" color={theme.textSecondary}>
          Classes
        </AppText>
      </View>
    </Pressable>
  );
}

/**
 * Class Card Component for Modal
 */
function ClassCard({
  classData,
  isAssigned,
  onToggle,
  isToggling,
}: { classData: ClassResponse; isAssigned: boolean; onToggle: () => void; isToggling: boolean }) {
  const theme = useTheme();
  const initials = classData.class_name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  
  return (
    <View style={styles.classCard}>
      <View style={[styles.classAvatar, isAssigned && { backgroundColor: BrandColors.teal }]}>
        <AppText variant="label" color={isAssigned ? '#fff' : theme.text}>
          {initials}
        </AppText>
      </View>
      
      <View style={styles.classInfo}>
        <AppText variant="body" style={styles.className}>
          {classData.class_name}
        </AppText>
        <AppText variant="caption" color={theme.textSecondary}>
          Capacity: {classData.capacity || 'Unlimited'}
        </AppText>
      </View>
      
      <Pressable
        onPress={onToggle}
        disabled={isToggling}
        style={[
          styles.toggleButton,
          isAssigned && styles.toggleButtonAssigned,
          isToggling && styles.toggleButtonDisabled,
        ]}
      >
        {isToggling ? (
          <ActivityIndicator size="small" color={isAssigned ? '#dc2626' : '#fff'} />
        ) : (
          <View style={styles.toggleContent}>
            <Icon
              name={isAssigned ? 'close-circle' : 'add-circle'}
              size={20}
              color="#fff"
            />
            <AppText variant="caption" color="#fff">
              {isAssigned ? 'Remove' : 'Add'}
            </AppText>
          </View>
        )}
      </Pressable>
    </View>
  );
}

/**
 * Main TermAssignments Component
 */
export function TermAssignments({
  schoolId,
  canManage = false,
  onAssignmentsChange,
}: {
  schoolId: number;
  canManage?: boolean;
  onAssignmentsChange?: () => void;
}) {
  const router = useRouter();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  
  const [selectedTermId, setSelectedTermId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showClassModal, setShowClassModal] = useState(false);
  
  // Queries
  const { data: terms, isLoading: isLoadingTerms } = useGetTermsBySchoolQuery(schoolId, {
    skip: !schoolId,
  });
  
  const { data: classes, isLoading: isLoadingClasses } = useListClassesQuery({ pageSize: 100 }, {
    skip: !showClassModal,
  });
  
  const { data: termClasses, isLoading: isLoadingTermClasses, refetch: refetchTermClasses } = useGetClassesByTermQuery(selectedTermId || 0, {
    skip: !selectedTermId,
  });
  
  // Mutations
  const [assignClass, { isLoading: isAssigning }] = useAssignClassToTermMutation();
  const [unassignClass, { isLoading: isUnassigning }] = useUnassignClassFromTermMutation();
  
  // Derived data
  const assignedClassIds = useMemo(
    () => new Set(termClasses?.map((c) => c.class_id) || []),
    [termClasses]
  );
  
  // Filter classes by school
  const filteredClasses = useMemo(() => {
    if (!classes?.data) return [];
    const schoolClasses = classes.data.filter((c) => c.school_id === schoolId);
    return schoolClasses.filter((c) =>
      c.class_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [classes, schoolId, searchQuery]);
  
  // Handlers
  const handleTermSelect = useCallback((termId: number) => {
    setSelectedTermId(termId);
  }, []);
  
  const handleClassToggle = useCallback(
    async (classId: number) => {
      if (!selectedTermId) return;
      
      try {
        if (assignedClassIds.has(classId)) {
          await unassignClass({ classId, termId: selectedTermId }).unwrap();
        } else {
          await assignClass({ classId, termId: selectedTermId }).unwrap();
        }
        refetchTermClasses();
        onAssignmentsChange?.();
      } catch (error) {
        console.error('Failed to update class assignment:', error);
      }
    },
    [selectedTermId, assignedClassIds, assignClass, unassignClass, refetchTermClasses, onAssignmentsChange]
  );
  
  const isLoading = isLoadingTerms;
  const isMutating = isAssigning || isUnassigning;
  
  // Loading state
  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color={BrandColors.coral} />
      </View>
    );
  }
  
  // Empty state
  if (!terms || terms.length === 0) {
    return (
      <View style={styles.emptyState}>
        <AppText style={styles.emptyStateIcon}>📅</AppText>
        <AppText variant="body" color={theme.textSecondary}>
          No terms found for this school
        </AppText>
        {canManage && (
          <Button
            label="Create Term"
            onPress={() => router.push('/manage/terms')}
            variant="secondary"
            style={{ marginTop: 16 }}
          />
        )}
      </View>
    );
  }
  
  const selectedTerm = terms.find((t) => t.term_id === selectedTermId);
  const termIsActive = selectedTerm ? isTermActive(selectedTerm) : false;
  
  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <AppText variant="subheading">
          Term Management
        </AppText>
        {canManage && (
          <Button
            label="Add Term"
            variant="ghost"
            onPress={() => router.push('/manage/terms')}
          />
        )}
      </View>
      
      {/* Info Banner */}
      {canManage && (
        <View style={styles.infoBanner}>
          <Icon name="information-circle" size={20} color={BrandColors.teal} />
          <AppText variant="body" style={{ flex: 1 }}>
            Select a term to manage class assignments. Active terms are highlighted.
          </AppText>
        </View>
      )}
      
      {/* Terms List */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.termsScroll}>
        <View style={styles.termsRow}>
          {terms.map((term) => (
            <TermCard
              key={term.term_id}
              term={term}
              classCount={selectedTermId === term.term_id ? (termClasses?.length || 0) : 0}
              isSelected={selectedTermId === term.term_id}
              onPress={() => handleTermSelect(term.term_id)}
            />
          ))}
        </View>
      </ScrollView>
      
      {/* Selected Term Details */}
      {selectedTermId && (
        <View style={styles.termDetails}>
          <View style={styles.termDetailsHeader}>
            <View>
              <AppText variant="subheading">
                {selectedTerm?.term_name}
              </AppText>
              <AppText variant="caption" color={theme.textSecondary}>
                {formatDate(selectedTerm?.start_date)} - {formatDate(selectedTerm?.end_date)}
              </AppText>
            </View>
            {canManage && (
              <Button
                label="Manage Classes"
                onPress={() => setShowClassModal(true)}
                disabled={!termIsActive}
              />
            )}
          </View>
          
          {/* Assigned Classes */}
          <View style={styles.assignedSection}>
            <AppText variant="label" color={theme.textSecondary}>
              Assigned Classes ({termClasses?.length || 0})
            </AppText>
            
            {isLoadingTermClasses ? (
              <ActivityIndicator size="small" color={BrandColors.coral} />
            ) : termClasses && termClasses.length > 0 ? (
              <View style={styles.assignedList}>
                {termClasses.map((cls) => (
                  <Pressable
                    key={cls.class_id}
                    onPress={() => router.push(`/class/${cls.class_id}`)}
                    style={styles.assignedClassChip}
                  >
                    <AppText variant="caption">{cls.class_name}</AppText>
                  </Pressable>
                ))}
              </View>
            ) : (
              <AppText variant="body" color={theme.textSecondary} style={{ marginTop: 8 }}>
                No classes assigned to this term
              </AppText>
            )}
          </View>
        </View>
      )}
      
      {/* Class Assignment Modal */}
      <Modal
        visible={showClassModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowClassModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <AppText variant="subheading">
                Manage Classes for {selectedTerm?.term_name}
              </AppText>
              <Pressable onPress={() => setShowClassModal(false)} style={styles.closeButton}>
                <Icon name="close" size={24} color={theme.text} />
              </Pressable>
            </View>
            
            {/* Search */}
            <View style={styles.searchContainer}>
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
            <ScrollView style={styles.classesList}>
              {isLoadingClasses ? (
                <ActivityIndicator size="large" color={BrandColors.coral} />
              ) : (
                filteredClasses.map((cls) => (
                  <ClassCard
                    key={cls.class_id}
                    classData={cls}
                    isAssigned={assignedClassIds.has(cls.class_id)}
                    onToggle={() => handleClassToggle(cls.class_id)}
                    isToggling={isMutating}
                  />
                ))
              )}
            </ScrollView>
            
            <Button
              label="Done"
              onPress={() => setShowClassModal(false)}
              style={{ marginTop: 16 }}
            />
          </View>
        </View>
      </Modal>
    </View>
  );
}
