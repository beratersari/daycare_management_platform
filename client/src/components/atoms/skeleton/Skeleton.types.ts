import { type ViewStyle } from 'react-native';

/**
 * Props for the Skeleton component.
 */
export interface SkeletonProps {
  /** Width of the skeleton. Can be a number or percentage string like '100%' */
  width?: number | string;
  /** Height of the skeleton. Can be a number or percentage string */
  height?: number | string;
  /** Border radius in pixels. Defaults to 8 */
  borderRadius?: number;
  /** Optional style overrides */
  style?: ViewStyle;
}
