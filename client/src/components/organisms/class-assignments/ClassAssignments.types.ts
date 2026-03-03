/**
 * Types for ClassAssignments component
 */

import type { ClassAssignmentsResponse, StudentAssignmentResponse, TeacherAssignmentResponse } from '@/store/api/classApi';

export interface ClassAssignmentsProps {
  /** The class ID to manage assignments for */
  classId: number;
  /** The class name for display */
  className: string;
  /** Optional term ID to filter assignments */
  termId?: number;
  /** Callback when assignments change */
  onAssignmentsChange?: () => void;
}

export interface AssignmentSectionProps {
  /** Title of the section */
  title: string;
  /** Count of items */
  count: number;
  /** Whether user can manage (add/remove) */
  canManage: boolean;
  /** Children elements */
  children: React.ReactNode;
}

export interface StudentAssignmentCardProps {
  /** Student assignment data */
  student: StudentAssignmentResponse;
  /** Whether user can remove */
  canRemove: boolean;
  /** Callback when remove is pressed */
  onRemove: () => void;
  /** Whether removal is in progress */
  isRemoving: boolean;
}

export interface TeacherAssignmentCardProps {
  /** Teacher assignment data */
  teacher: TeacherAssignmentResponse;
  /** Whether user can remove */
  canRemove: boolean;
  /** Callback when remove is pressed */
  onRemove: () => void;
  /** Whether removal is in progress */
  isRemoving: boolean;
}

export interface AvailableStudentCardProps {
  /** Student ID */
  studentId: number;
  /** Student name */
  studentName: string;
  /** Whether student is already assigned */
  isAssigned: boolean;
  /** Whether assignment is at capacity */
  atCapacity: boolean;
  /** Callback when pressed */
  onPress: () => void;
  /** Whether operation is in progress */
  isLoading: boolean;
}

export interface AvailableTeacherCardProps {
  /** Teacher ID */
  teacherId: number;
  /** Teacher name */
  teacherName: string;
  /** Whether teacher is already assigned */
  isAssigned: boolean;
  /** Callback when pressed */
  onPress: () => void;
  /** Whether operation is in progress */
  isLoading: boolean;
}

export interface CapacityIndicatorProps {
  /** Current number of students */
  current: number;
  /** Maximum capacity (undefined for unlimited) */
  capacity?: number | null;
  /** Size variant */
  size?: 'small' | 'medium' | 'large';
}
