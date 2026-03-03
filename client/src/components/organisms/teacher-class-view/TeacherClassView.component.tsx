/**
 * Organism — TeacherClassView
 *
 * Simplified class view for teachers showing their assigned classes
 * and the students in each class. Teachers can view but not modify assignments.
 */
import React from 'react';
import { View, ScrollView, Pressable } from 'react-native';
import { useRouter } from 'expo-router';

import { AppText } from '@/components/atoms/app-text';
import { Icon } from '@/components/atoms/icon';
import { LoadingState } from '@/components/molecules/loading-state';
import { EmptyState } from '@/components/molecules/empty-state';
import { useTheme } from '@/hooks/use-theme';
import { useLocalization } from '@/hooks/use-localization';
import { useGetTeacherClassesQuery } from '@/store/api/teacherApi';
import { useGetClassAssignmentsQuery } from '@/store/api/classApi';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { BrandColors } from '@/constants/theme';

import { styles } from './TeacherClassView.styles';

interface ClassCardProps {
  classId: number;
  className: string;
  studentCount: number;
  teacherCount: number;
  onPress: () => void;
}

function ClassCard({ classId, className, studentCount, teacherCount, onPress }: ClassCardProps) {
  const theme = useTheme();
  
  return (
    <Pressable
      onPress={onPress}
      style={[styles.classCard, { backgroundColor: '#fff' }]}
    >
      <View style={styles.classHeader}>
        <View style={styles.classIcon}>
          <Icon name="library" size={24} color="#fff" />
        </View>
        <View style={styles.classInfo}>
          <AppText variant="subheading" style={styles.className}>
            {className}
          </AppText>
          <AppText variant="caption" color={theme.textSecondary}>
            Class #{classId}
          </AppText>
        </View>
        <Icon name="chevron-forward" size={20} color={theme.textSecondary} />
      </View>
      
      <View style={styles.classStats}>
        <View style={styles.statBadge}>
          <Icon name="people" size={16} color={BrandColors.coral} />
          <AppText variant="body" style={{ fontWeight: '600' }}>
            {studentCount}
          </AppText>
          <AppText variant="caption" color={theme.textSecondary}>
            Students
          </AppText>
        </View>
        
        <View style={styles.statBadge}>
          <Icon name="school" size={16} color={BrandColors.teal} />
          <AppText variant="body" style={{ fontWeight: '600' }}>
            {teacherCount}
          </AppText>
          <AppText variant="caption" color={theme.textSecondary}>
            Teachers
          </AppText>
        </View>
      </View>
    </Pressable>
  );
}

interface StudentListItemProps {
  name: string;
  avatar?: string;
  index: number;
}

function StudentListItem({ name, index }: StudentListItemProps) {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
    
  const colors = ['#F26076', '#458B73', '#FF9760', '#FFD150'];
  const bgColor = colors[index % colors.length];
  
  return (
    <View style={styles.studentItem}>
      <View style={[styles.studentAvatar, { backgroundColor: bgColor }]}>
        <AppText variant="label" color="#fff">
          {initials}
        </AppText>
      </View>
      <AppText variant="body" style={{ flex: 1 }}>
        {name}
      </AppText>
    </View>
  );
}

export function TeacherClassView() {
  const router = useRouter();
  const theme = useTheme();
  const { t } = useLocalization();
  const user = useAppSelector(selectCurrentUser);
  
  const { data: classes, isLoading: isLoadingClasses } = useGetTeacherClassesQuery(user?.user_id || 0, {
    skip: !user?.user_id,
  });
  
  if (isLoadingClasses) {
    return <LoadingState cardCount={2} />;
  }
  
  if (!classes || classes.length === 0) {
    return (
      <EmptyState
        icon="📚"
        message="No Classes Assigned"
        subtitle="You are not currently assigned to any classes."
      />
    );
  }
  
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <AppText variant="label" color={theme.textSecondary} style={styles.sectionTitle}>
        My Classes ({classes.length})
      </AppText>
      
      {classes.map((cls) => (
        <ClassCard
          key={cls.class_id}
          classId={cls.class_id}
          className={cls.class_name}
          studentCount={cls.students?.length || 0}
          teacherCount={cls.teachers?.length || 0}
          onPress={() => router.push(`/class/${cls.class_id}`)}
        />
      ))}
    </ScrollView>
  );
}

interface SingleClassViewProps {
  classId: number;
}

export function TeacherSingleClassView({ classId }: SingleClassViewProps) {
  const theme = useTheme();
  const { data: assignments, isLoading } = useGetClassAssignmentsQuery({ classId });
  
  if (isLoading) {
    return <LoadingState cardCount={2} />;
  }
  
  return (
    <View style={styles.singleClassContainer}>
      {/* Students Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Icon name="people" size={20} color={BrandColors.coral} />
          <AppText variant="subheading">
            Students ({assignments?.students.length || 0})
          </AppText>
        </View>
        
        {assignments?.students && assignments.students.length > 0 ? (
          <View style={styles.studentList}>
            {assignments.students.map((student, index) => (
              <StudentListItem
                key={student.student_id}
                name={student.student_name || `Student #${student.student_id}`}
                index={index}
              />
            ))}
          </View>
        ) : (
          <View style={styles.emptySection}>
            <AppText variant="body" color={theme.textSecondary}>
              No students in this class
            </AppText>
          </View>
        )}
      </View>
      
      {/* Teachers Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Icon name="school" size={20} color={BrandColors.teal} />
          <AppText variant="subheading">
            Teachers ({assignments?.teachers.length || 0})
          </AppText>
        </View>
        
        {assignments?.teachers && assignments.teachers.length > 0 ? (
          <View style={styles.teacherList}>
            {assignments.teachers.map((teacher, index) => (
              <View key={teacher.teacher_id} style={styles.teacherItem}>
                <View
                  style={[
                    styles.teacherAvatar,
                    { backgroundColor: BrandColors.teal },
                  ]}
                >
                  <AppText variant="label" color="#fff">
                    {teacher.teacher_name
                      ?.split(' ')
                      .map((n) => n[0])
                      .join('')
                      .slice(0, 2)
                      .toUpperCase() || 'T'}
                  </AppText>
                </View>
                <AppText variant="body" style={{ flex: 1 }}>
                  {teacher.teacher_name || `Teacher #${teacher.teacher_id}`}
                </AppText>
              </View>
            ))}
          </View>
        ) : (
          <View style={styles.emptySection}>
            <AppText variant="body" color={theme.textSecondary}>
              No teachers assigned to this class
            </AppText>
          </View>
        )}
      </View>
    </View>
  );
}
