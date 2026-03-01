import React from 'react';

/**
 * Props for the ScreenTemplate component.
 */
export interface ScreenTemplateProps {
  /** Header component (typically PageHeader molecule) */
  header?: React.ReactNode;
  /** Main content to render inside the template */
  children: React.ReactNode;
  /** Whether content should scroll. Defaults to true */
  scrollable?: boolean;
  /** Additional padding for content area */
  contentPadding?: number;
}
