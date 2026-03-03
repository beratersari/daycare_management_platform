/**
 * Organism — ParentClassView
 *
 * View for parents to see their children's class assignments.
 * Read-only view showing class details, teachers, and classmates.
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
import { useGetMyStudentsQuery } from '@/store/api/teacherApi';
import { useGetClassAssignmentsQuery } from '@/store/api/classApi';
import { useAppSelector } from '@/store/hooks';
import { selectCurrentUser } from '@/store/authSlice';
import { BrandColors } from '@/constants/theme';

import { styles } from './ParentClassView.styles';

interface ChildClassCardProps {
  childName: string;
  classId: number;
  className: string;
  teacherName?: string;
  studentCount: number;
  onPress: () => void;
}

function ChildClassCard({
  childName,
  className,
  teacherName,
  studentCount,
  onPress,
}: ChildClassCardProps) {
  const theme = useTheme();
  
  return (
    <Pressable onPress={onPress} style={styles.childCard}>
      <View style={styles.childHeader}>
        <View style={styles.childAvatar}>
          <AppText variant="label" color="#fff">
            {childName.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()}
          </AppText>
        </View>
        <View style={styles.childInfo}>
          <AppText variant="body" color={theme.textSecondary}>
            {childName}
          </AppText>
          <AppText variant="subheading" style={styles.className}>
            {className}
          </AppText>
        </View>
        <Icon name="chevron-forward" size={20} color={theme.textSecondary} />
      </View>
      
      <View style={styles.classDetails}>
        {teacherName && (
          <View style={styles.detailItem}>
            <Icon name="school" size={16} color={BrandColors.teal} />
            <AppText variant="caption" color={theme.textSecondary}>
              Teacher: {teacherName}
            </AppText>
          </View>
        )}
        <View style={styles.detailItem}>
          <Icon name="people" size={16} color={BrandColors.coral} />
          <AppText variant="caption" color={theme.textSecondary}>
            {studentCount} students in class
          </AppText>
        </View>
      </View>
    </Pressable>
  );
}

interface ClassDetailViewProps {
  classId: number;
  childName: string;
}

export function ParentClassDetailView({ classId, childName }: ClassDetailViewProps) {
  const theme = useTheme();
  const { data: assignments, isLoading } = useGetClassAssignmentsQuery({ classId });
  
  if (isLoading) {
    return <LoadingState cardCount={2} />;
  }
  
  const mainTeacher = assignments?.teachers[0];
  
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Child Info Banner */}
      <View style={styles.childBanner}>
        <View style={styles.childBannerAvatar}>
          <AppText variant="label" color="#fff">
            {childName.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()}
          </AppText>
        </View>
        <View>
          <AppText variant="caption" color={theme.textSecondary}>
            Viewing class for
          </AppText>
          <AppText variant="subheading">{childName}</AppText>
        </View>
      </View>
      
      {/* Class Info */}
      <View style={styles.infoCard}>
        <AppText variant="subheading" style={{ marginBottom: 12 }}>
          {assignments?.class_name || 'Class'}
        </AppText>
        
        <View style={styles.infoRow}>
          <View style={styles.infoItem}>
            <Icon name="people" size={20} color={BrandColors.coral} />
            <AppText variant="display" color={BrandColors.coral}>
              {assignments?.students.length || 0}
            </AppText>
            <AppText variant="caption" color={theme.textSecondary}>
              Students
            </AppText>
          </View>
          
          <View style={styles.infoItem}>
            <Icon name="school" size={20} color={BrandColors.teal} />
            <AppText variant="display" color={BrandColors.teal}>
              {assignments?.teachers.length || 0}
            </AppText>
            <AppText variant="caption" color={theme.textSecondary}>
              Teachers
            </AppText>
          </View>
        </View>
        
        {assignments?.capacity !== null && assignments?.capacity !== undefined && (
          <View style={styles.capacityInfo}>
            <AppText variant="caption" color={theme.textSecondary}>
              Class Capacity: {assignments.current_student_count}/{assignments.capacity}
            </AppText>
            <View style={styles.capacityBar}>
              <View
                style={[
                  styles.capacityFill,
                  {
                    width: `${Math.min(
                      ((assignments.current_student_count || 0) / assignments.capacity) * 100,
                      100
                    )}%`,
                  },
                ]}
              />
            </View>
          </View>
        )}
      </View>
      
      {/* Teachers Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Icon name="school" size={20} color={BrandColors.teal} />
          <AppText variant="subheading">Teachers</AppText>
        </View>
        
        {assignments?.teachers && assignments.teachers.length > 0 ? (
          assignments.teachers.map((teacher) => (
            <View key={teacher.teacher_id} style={styles.teacherCard}>
              <View style={styles.teacherAvatar}>
                <AppText variant="label" color="#fff">
                  {teacher.teacher_name
                    ?.split(' ')
                    .map((n) => n[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase() || 'T'}
                </AppText>
              </View>
              <View style={styles.teacherInfo}>
                <AppText variant="body" style={{ fontWeight: '600' }}>
                  {teacher.teacher_name || `Teacher #${teacher.teacher_id}`}
                </AppText>
                <AppText variant="caption" color={theme.textSecondary}>
                  Primary Teacher
                </AppText>
              </View>
            </View>
          ))
        ) : (
          <View style={styles.emptyCard}>
            <AppText variant="body" color={theme.textSecondary}>
              No teacher information available
            </AppText>
          </View>
        )}
      </View>
      
      {/* Classmates Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Icon name="people" size={20} color={BrandColors.coral} />
          <AppText variant="subheading">Classmates</AppText>
          <AppText variant="caption" color={theme.textSecondary}>
            ({assignments?.students.length || 0} students)
          </AppText>
        </View>
        
        {assignments?.students && assignments.students.length > 0 ? (
          <View style={styles.classmatesGrid}>
            {assignments.students.map((student, index) => {
              const isMyChild = student.student_name === childName;
              const colors = ['#F26076', '#458B73', '#FF9760', '#FFD150', '#8b5cf6', '#ec4899'];
              const bgColor = colors[index % colors.length];
              
              return (
                <View
                  key={student.student_id}
                  style={[
                    styles.classmateItem,
                    isMyChild && styles.myChildItem,
                  ]}
                >
                  <View style={[styles.classmateAvatar, { backgroundColor: bgColor }]}>
                    <AppText variant="caption" color="#fff">
                      {student.student_name
                        ?.split(' ')
                        .map((n) => n[0])
                        .join('')
                        .slice(0, 2)
                        .toUpperCase() || 'S'}
                    </AppText>
                  </View>
                  <AppText
                    variant="caption"
                    style={[styles.classmateName, isMyChild && styles.myChildName]}
                    numberOfLines={1}
                  >
                    {student.student_name || `Student #${student.student_id}`}
                    {isMyChild && ' (Your Child)'}
                  </AppText>
                </View>
              );
            })}
          </View>
        ) : (
          <View style={styles.emptyCard}>
            <AppText variant="body" color={theme.textSecondary}>
              No student information available
            </AppText>
          </View>
        )}
      </View>
      
      {/* Contact Info */}
      <View style={styles.contactCard}>
        <Icon name="information-circle" size={20} color={BrandColors.coral} />
        <AppText variant="body" style={{ flex: 1 }}>
          Need to contact the teacher? Reach out through the school office or messaging system.
        </AppText>
      </View>
    </ScrollView>
  );
}

export function ParentClassView() {
  const router = useRouter();
  const theme = useTheme();
  const user = useAppSelector(selectCurrentUser);
  
  const { data: students, isLoading } = useGetMyStudentsQuery();
  
  if (isLoading) {
    return <LoadingState cardCount={2} />;
  }
  
  if (!students || students.length === 0) {
    return (
      <EmptyState
        icon="👨‍👩‍👧‍👦"
        message="No Children Linked"
        subtitle="Your account is not linked to any children."
      />
    );
  }
  
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <AppText variant="label" color={theme.textSecondary} style={styles.sectionTitle}>
        My Children ({students.length})
      </AppText>
      
      {students.map((student) => (
        <ChildClassCard
          key={student.student_id}
          childName={`${student.first_name} ${student.last_name}`}
          classId={student.class_ids?.[0] || 0}
          className={student.class_ids?.length > 0 ? 'View Class' : 'Not Enrolled'}
          studentCount={0}
          onPress={() => {
            if (student.class_ids?.[0]) {
              router.push(`/class/${student.class_ids[0]}`);
            }
          }}
        />
      ))}
    </ScrollView>
  );
}
