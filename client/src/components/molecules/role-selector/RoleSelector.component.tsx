/**
 * Molecule — RoleSelector
 *
 * A segmented control for selecting user roles during registration.
 * Displays available roles as selectable segments with visual feedback.
 *
 * @example
 * ```tsx
 * <RoleSelector
 *   value="PARENT"
 *   onChange={(role) => setRole(role)}
 *   disabled={isLoading}
 * />
 * ```
 */
import React from 'react';
import { Pressable, View } from 'react-native';

import { AppText } from '@/components/atoms/app-text';
import { useTheme } from '@/hooks/use-theme';
import type { UserRole } from '@/store/api/authApi';
import { RoleSelectorProps } from './RoleSelector.types';
import { styles } from './RoleSelector.styles';

/** Roles that end-users can self-register as */
export const SELECTABLE_ROLES: UserRole[] = ['TEACHER', 'PARENT'];

/** Display labels for each role */
const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: 'Admin',
  DIRECTOR: 'Director',
  TEACHER: 'Teacher',
  PARENT: 'Parent',
};

/** Label for the account type field */
const FIELD_LABEL = 'Account Type';

/** Color for selected segment text */
const SELECTED_TEXT_COLOR = '#fff';

export function RoleSelector({
  value,
  onChange,
  disabled = false,
  roles = SELECTABLE_ROLES,
}: RoleSelectorProps) {
  const theme = useTheme();

  const handlePress = (role: UserRole) => {
    if (!disabled) {
      onChange(role);
    }
  };

  return (
    <View style={styles.wrapper}>
      <AppText variant="label" color={theme.textSecondary} style={styles.label}>
        {FIELD_LABEL}
      </AppText>

      <View style={[styles.track, { backgroundColor: theme.backgroundElement }]}>
        {roles.map((role, index) => {
          const isSelected = role === value;
          const isFirst = index === 0;
          const isLast = index === roles.length - 1;

          return (
            <Pressable
              key={role}
              onPress={() => handlePress(role)}
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
                color={isSelected ? SELECTED_TEXT_COLOR : theme.textSecondary}
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
