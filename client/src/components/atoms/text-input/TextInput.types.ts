import { type TextInputProps, type TextInput } from 'react-native';

/**
 * Props for the AppTextInput component.
 */
export interface AppTextInputProps extends TextInputProps {
  /** Optional label displayed above the input */
  label?: string;
  /** Optional error message displayed below the input */
  error?: string;
  /** Whether to render a show/hide toggle for password fields. Defaults to false */
  secureToggle?: boolean;
}
