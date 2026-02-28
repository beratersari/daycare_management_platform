/**
 * Molecule — RoleSelector
 *
 * A horizontal segmented control that lets the user pick their account role.
 * Only TEACHER and PARENT are exposed for self-registration; ADMIN and
 * DIRECTOR accounts are created by system administrators.
 *
 * Props
 *   value      — currently selected role
 *   onChange   — called with the new role when a segment is tapped
 *   disabled   — greys out all segments (e.g. while a request is in-flight)
 */
import React from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/atoms/AppText';
import { useTheme } from '@/hooks/use-theme';
import { BrandColors } from '@/constants/theme';
import type { UserRole } from '@/store/api/authApi';

/** Roles that end-users can self-register as. */
export const SELECTABLE_ROLES: UserRole[] = ['TEACHER', 'PARENT'];

const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: 'Admin',
  DIRECTOR: 'Director',
  TEACHER: 'Teacher',
  PARENT: 'Parent',
};

// Use brand color for selection
const BRAND = BrandColors.coral;

interface RoleSelectorProps {
  value: UserRole;
  onChange: (role: UserRole) => void;
  disabled?: boolean;
  /** Override which roles appear (defaults to SELECTABLE_ROLES) */
  roles?: UserRole[];
}

export function RoleSelector({
  value,
  onChange,
  disabled = false,
  roles = SELECTABLE_ROLES,
}: RoleSelectorProps) {
  const theme = useTheme();

  return (
    <View style={styles.wrapper}>
      <AppText variant="label" color={theme.textSecondary} style={styles.label}>
        Account Type
      </AppText>

      <View
        style={[
          styles.track,
          { backgroundColor: theme.backgroundElement },
        ]}>
        {roles.map((role, idx) => {
          const isSelected = role === value;
          const isFirst = idx === 0;
          const isLast = idx === roles.length - 1;

          return (
            <Pressable
              key={role}
              onPress={() => !disabled && onChange(role)}
              style={[
                styles.segment,
                isFirst && styles.segmentFirst,
                isLast && styles.segmentLast,
                isSelected && styles.segmentSelected,
                disabled && styles.segmentDisabled,
              ]}
              accessibilityRole="radio"
              accessibilityState={{ checked: isSelected, disabled }}>
              <AppText
                variant="caption"
                color={isSelected ? '#fff' : theme.textSecondary}
                style={[styles.segmentLabel, isSelected && styles.segmentLabelSelected]}>
                {ROLE_LABELS[role]}
              </AppText>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    gap: 6,
    alignSelf: 'stretch',
  },
  label: {
    marginLeft: 2,
  },
  track: {
    flexDirection: 'row',
    borderRadius: 12,
    padding: 4,
    gap: 4,
  },
  segment: {
    flex: 1,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 9,
  },
  segmentFirst: {
    borderTopLeftRadius: 9,
    borderBottomLeftRadius: 9,
  },
  segmentLast: {
    borderTopRightRadius: 9,
    borderBottomRightRadius: 9,
  },
  segmentSelected: {
    backgroundColor: BRAND,
  },
  segmentDisabled: {
    opacity: 0.5,
  },
  segmentLabel: {
    fontWeight: '500',
  },
  segmentLabelSelected: {
    fontWeight: '700',
  },
});
