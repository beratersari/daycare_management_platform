/**
 * Alert type determining the visual style of the banner.
 * - 'error': Red styling for error messages
 * - 'success': Green styling for success messages
 * - 'info': Blue styling for informational messages
 */
export type AlertType = 'error' | 'success' | 'info';

/**
 * Props for the AlertBanner component.
 */
export interface AlertBannerProps {
  /** The type of alert which determines the color scheme */
  type: AlertType;
  /** The message to display in the banner */
  message: string;
}
