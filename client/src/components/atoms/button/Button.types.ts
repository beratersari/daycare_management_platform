import { type PressableProps, type ViewStyle } from 'react-native';

/**
 * Button variant determining the visual style.
 * - 'primary': Filled button with brand color background
 * - 'secondary': Outlined button with transparent background
 * - 'ghost': Text-only button with no background
 */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost';

/**
 * Props for the Button component.
 */
export interface ButtonProps extends PressableProps {
  /** The text label displayed on the button */
  label: string;
  /** Visual style variant. Defaults to 'primary' */
  variant?: ButtonVariant;
  /** Whether to show a loading indicator. Defaults to false */
  isLoading?: boolean;
  /** Whether the button should take full width. Defaults to true */
  fullWidth?: boolean;
  /** Optional style overrides for the button container */
  style?: ViewStyle;
}
