import { type ViewStyle } from 'react-native';
import { type Ionicons } from '@expo/vector-icons';

/**
 * Icon names from Ionicons icon family.
 * Using Ionicons as the primary icon set for consistency.
 */
export type IconName = keyof typeof Ionicons.glyphMap;

export interface IconProps {
  /** Icon name from Ionicons */
  name: IconName;
  /** Icon size in pixels */
  size?: number;
  /** Icon color */
  color?: string;
  /** Optional style overrides */
  style?: ViewStyle;
}