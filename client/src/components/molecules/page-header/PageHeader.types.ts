import React from 'react';

/**
 * Props for the PageHeader component.
 */
export interface PageHeaderProps {
  /** The title displayed in the center of the header */
  title: string;
  /** Callback function invoked when the back button is pressed */
  onBack: () => void;
  /** Optional element rendered on the right side of the header */
  rightElement?: React.ReactNode;
}
