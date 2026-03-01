import { type ViewProps } from 'react-native';

/**
 * Props for the EventCard component.
 */
export interface EventCardProps extends ViewProps {
  /** Event title */
  title: string;
  /** Event date string */
  eventDate: string;
  /** Name of the class this event belongs to */
  className: string;
  /** Optional event description */
  description?: string | null;
  /** Optional photo URL for the event */
  photoUrl?: string | null;
  /** Whether the card is pressable */
  onPress?: () => void;
}
