import { type TextProps } from 'react-native';

/**
 * Text variant determining the font size and weight.
 * - 'display': Large text for hero sections (32px, bold)
 * - 'heading': Section headings (22px, bold)
 * - 'subheading': Subsection headings (17px, semibold)
 * - 'body': Body text (15px, regular)
 * - 'caption': Small text for metadata (13px, regular)
 * - 'label': Form labels (13px, semibold, uppercase)
 * - 'error': Error messages (13px, medium)
 */
export type TextVariant =
  | 'display'
  | 'heading'
  | 'subheading'
  | 'body'
  | 'caption'
  | 'label'
  | 'error';

/**
 * Props for the AppText component.
 */
export interface AppTextProps extends TextProps {
  /** Text variant determining font size and weight. Defaults to 'body' */
  variant?: TextVariant;
  /** Text color. Defaults to theme text color (or red for error variant) */
  color?: string;
}
