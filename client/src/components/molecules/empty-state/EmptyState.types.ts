import { type IconName } from '@/components/atoms/icon';

/**
 * Props for the EmptyState component.
 */
export interface EmptyStateProps {
  /** Main message to display, describing the empty state */
  message: string;
  /** Optional icon name from Ionicons. Takes precedence over emoji if both provided */
  icon?: IconName;
  /** Optional emoji string to display as an icon. Used if icon is not provided */
  emoji?: string;
  /** Optional subtitle providing additional context */
  subtitle?: string;
}
