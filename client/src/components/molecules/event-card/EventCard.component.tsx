/**
 * Molecule — EventCard
 *
 * A family-friendly card component for displaying event information.
 * Features colorful gradients, rounded corners, and an inviting design.
 *
 * @example
 * ```tsx
 * <EventCard
 *   title="Field Trip to Zoo"
 *   eventDate="2024-03-15T10:00:00"
 *   className="Sunflower Room"
 *   description="We will visit the zoo on Friday. Please bring lunch."
 *   onPress={() => console.log('Event pressed')}
 * />
 * ```
 */
import React from 'react';
import { View, Pressable, Image } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { Icon } from '@/components/atoms/icon';
import { useTheme } from '@/hooks/use-theme';
import { BrandColors } from '@/constants/theme';
import { EventCardProps } from './EventCard.types';
import { styles } from './EventCard.styles';

// Array of brand colors for the gradient backgrounds
const CARD_COLORS = [
  BrandColors.coral,
  BrandColors.orange,
  BrandColors.yellow,
  BrandColors.teal,
];

/**
 * Get a color for the event card based on the event title
 */
function getEventColor(title: string): string {
  const hash = title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return CARD_COLORS[hash % CARD_COLORS.length];
}

/**
 * Format date for display
 */
function formatEventDate(dateString: string): { day: string; month: string; time: string } {
  const date = new Date(dateString);
  const day = date.getDate().toString();
  const month = date.toLocaleString('en-US', { month: 'short' });
  const time = date.toLocaleString('en-US', { hour: 'numeric', minute: '2-digit' });
  return { day, month, time };
}

export function EventCard({
  title,
  eventDate,
  className,
  description,
  photoUrl,
  onPress,
  style,
  ...rest
}: EventCardProps) {
  const theme = useTheme();
  const eventColor = getEventColor(title);
  const { day, month, time } = formatEventDate(eventDate);

  const renderContent = () => (
    <>
      {/* Image or Gradient Placeholder */}
      <View style={[styles.imageContainer, { backgroundColor: eventColor + '30' }]}>
        {photoUrl ? (
          <Image source={{ uri: photoUrl }} style={styles.eventImage} resizeMode="cover" />
        ) : (
          <View style={[styles.placeholderGradient, { backgroundColor: eventColor + '20' }]}>
            <Icon name="calendar" size={40} color={eventColor} />
          </View>
        )}
      </View>

      {/* Content */}
      <View style={[styles.contentContainer, { backgroundColor: theme.backgroundElement }]}>
        <View style={styles.headerRow}>
          <View style={styles.title}>
            <AppText variant="subheading" numberOfLines={2}>
              {title}
            </AppText>
          </View>
          <View style={[styles.dateBadge, { backgroundColor: eventColor + '20' }]}>
            <AppText variant="caption" style={[styles.dateMonth, { color: eventColor }]}>
              {month}
            </AppText>
            <AppText variant="heading" style={[styles.dateDay, { color: eventColor }]}>
              {day}
            </AppText>
          </View>
        </View>

        {/* Class Badge */}
        <View style={styles.classBadge}>
          <Icon name="library" size={14} color={theme.textSecondary} style={styles.classIcon} />
          <AppText variant="caption" color={theme.textSecondary}>
            {className}
          </AppText>
          <AppText variant="caption" color={theme.textSecondary}> • {time}</AppText>
        </View>

        {/* Description */}
        {description && (
          <AppText variant="body" color={theme.textSecondary} style={styles.description} numberOfLines={3}>
            {description}
          </AppText>
        )}
      </View>
    </>
  );

  if (onPress) {
    return (
      <Pressable
        style={({ pressed }) => [
          styles.container,
          pressed && styles.pressed,
          style,
        ]}
        onPress={onPress}
        accessibilityRole="button"
        accessibilityLabel={title}
        {...rest}
      >
        {renderContent()}
      </Pressable>
    );
  }

  return (
    <View style={[styles.container, style]} {...rest}>
      {renderContent()}
    </View>
  );
}
