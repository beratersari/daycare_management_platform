/**
 * Types for TermAssignments component
 */

import type { TermResponse, TermClassResponse } from '@/store/api/termApi';

export interface TermAssignmentsProps {
  /** The term ID to manage assignments for */
  termId: number;
  /** The school ID to filter classes */
  schoolId?: number;
  /** Whether the user can manage assignments */
  canManage?: boolean;
  /** Callback when assignments change */
  onAssignmentsChange?: () => void;
}

export interface TermCardProps {
  /** Term data */
  term: TermResponse;
  /** Class count */
  classCount: number;
  /** Whether this term is selected */
  isSelected?: boolean;
  /** Press handler */
  onPress: () => void;
}

export interface ClassCardProps {
  /** Class data */
  classData: TermClassResponse;
  /** Whether the class is assigned */
  isAssigned: boolean;
  /** Callback when toggle is pressed */
  onToggle: () => void;
  /** Whether operation is in progress */
  isToggling: boolean;
}
