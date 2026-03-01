import { type IconName } from '@/components/atoms/icon';

/**
 * Color variant for the DashboardButton.
 * Maps to brand colors defined in the theme.
 * - 'coral': Primary accent color (#F26076)
 * - 'orange': Secondary accent color (#FF9760)
 * - 'yellow': Tertiary accent color (#FFD150)
 * - 'teal': Success/action color (#458B73)
 */
export type ButtonColorVariant = 'coral' | 'orange' | 'yellow' | 'teal';

/**
 * Props for the DashboardButton component.
 */
export interface DashboardButtonProps {
  /** The text label displayed on the button */
  label: string;
  /** Optional icon name from the Ionicons icon family */
  icon?: IconName;
  /** Color variant determining the button's background color. Defaults to 'coral' */
  colorVariant?: ButtonColorVariant;
  /** Callback function invoked when the button is pressed. If undefined, button is disabled */
  onPress?: () => void;
  /** Whether the button is disabled. Defaults to false */
  disabled?: boolean;
}
