/**
 * Props for the LoadingState component.
 */
export interface LoadingStateProps {
  /** Number of card skeletons to display. Defaults to 3 */
  cardCount?: number;
  /** Height of each card skeleton in pixels. Defaults to 80 */
  cardHeight?: number;
}

/**
 * Props for the ProfileLoadingState component.
 */
export interface ProfileLoadingStateProps {
  /** Whether to show the avatar skeleton. Defaults to true */
  showAvatar?: boolean;
}

/**
 * Props for the DashboardLoadingState component.
 */
export interface DashboardLoadingStateProps {
  /** Whether to show the quick actions section. Defaults to true */
  showQuickActions?: boolean;
}
