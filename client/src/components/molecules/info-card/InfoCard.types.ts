import React from 'react';

/**
 * Props for the InfoCard component.
 */
export interface InfoCardProps {
  /** The main title displayed at the top of the card */
  title: string;
  /** Optional subtitle displayed below the title */
  subtitle?: string;
  /** Optional content rendered below the header section */
  children?: React.ReactNode;
  /** Optional element rendered on the right side of the header */
  rightElement?: React.ReactNode;
  /** Optional callback - if provided, the card becomes pressable */
  onPress?: () => void;
}
